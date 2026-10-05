import hashlib
import json
import os
import re
import shutil
import sqlite3
import struct
import uuid
import time
from pathlib import Path
from datetime import datetime, timezone

STATES = {'ai_translated', 'needs_review', 'manual_verified', 'manual_locked',
          'source_changed', 'semantic_review', 'removed'}
PROTECTED = {'manual_verified', 'manual_locked'}

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()

def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('Duplicate key: ' + key)
        out[key] = value
    return out

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        retry_io(lambda: os.replace(temp, path))
    finally:
        if temp.exists(): temp.unlink()

def retry_io(action):
    # OneDrive/antivirus may briefly hold a new file/directory on Windows.
    for attempt in range(5):
        try: return action()
        except PermissionError:
            if attempt==4: raise
            time.sleep(.1*(attempt+1))

def load_source(root):
    root = Path(root)
    m = read_json(root / 'NewTextMap_en.json')
    b = (root / 'Compress_en.bin').read_bytes()
    if set(k for k in m if k.startswith('_')) != {'_count', '_version'}:
        raise ValueError('Unknown localization metadata')
    if len(b) < 4 or struct.unpack('<I', b[:4])[0] != m['_version']:
        raise ValueError('Localization version/header mismatch')
    rows = {}
    for key, loc in m.items():
        if key.startswith('_'): continue
        if not re.fullmatch(r'-?\d+', key) or not isinstance(loc, list) or len(loc) != 2:
            raise ValueError('Unknown key or localization format: ' + key)
        offset, size = loc
        if type(offset) is not int or type(size) is not int or offset < 4 or size < 0 or offset + size > len(b):
            raise ValueError('Invalid localization bounds: ' + key)
        rows[key] = b[offset:offset+size].decode('utf-8', errors='strict')
    if len(rows) != m['_count'] or not rows:
        raise ValueError('Localization count mismatch')
    return rows, m

def encode_source(source_dir, translations, destination):
    source, meta = load_source(source_dir)
    if set(source) != set(translations): raise ValueError('Missing/extra translation keys')
    output = Path(destination); output.mkdir(parents=True, exist_ok=True)
    binary = bytearray(struct.pack('<I', meta['_version']))
    mapping = {'_version': meta['_version'], '_count': len(source)}
    cache = {}
    for key in source:
        text = translations[key]
        if text not in cache:
            raw = text.encode('utf-8', errors='strict')
            cache[text] = [len(binary), len(raw)]; binary.extend(raw)
        mapping[key] = cache[text]
    (output / 'Compress_en.bin').write_bytes(binary)
    write_json(output / 'NewTextMap_en.json', mapping)
    actual, _ = load_source(output)
    if actual != translations: raise ValueError('Localization roundtrip failed')

def snapshot(work, build, source_dir, provenance):
    if not re.fullmatch(r'\d+', str(build)): raise ValueError('Invalid build')
    load_source(source_dir)
    target = Path(work) / 'builds' / str(build)
    hashes = {n: digest((Path(source_dir)/n).read_bytes()) for n in ('NewTextMap_en.json','Compress_en.bin')}
    if target.exists():
        info = read_json(target/'metadata.json')
        if info['hashes'] != hashes: raise ValueError('Immutable snapshot differs for same build')
        for n, h in hashes.items():
            if digest((target/'source'/n).read_bytes()) != h: raise ValueError('Corrupt snapshot')
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = target.with_name('.' + target.name + '-' + uuid.uuid4().hex)
    try:
        (stage/'source').mkdir(parents=True)
        for n in hashes: shutil.copy2(Path(source_dir)/n, stage/'source'/n)
        write_json(stage/'metadata.json', {'build':str(build),'hashes':hashes,'provenance':provenance,'created':now()})
        retry_io(lambda: stage.rename(target))
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return target

class Memory:
    def __init__(self, work, create=False):
        self.work = Path(work); self.path = self.work/'memory.sqlite3'
        if create:
            self.work.mkdir(parents=True, exist_ok=True)
            if self.path.exists(): raise ValueError('Memory already exists')
        elif not self.path.exists(): raise ValueError('Initialize Translation Memory first')
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        if create:
            self.db.executescript('''
                CREATE TABLE entries(key TEXT PRIMARY KEY, source_en TEXT NOT NULL, source_hash TEXT NOT NULL,
                    translation_sk TEXT NOT NULL, status TEXT NOT NULL, origin TEXT NOT NULL,
                    first_seen_build TEXT NOT NULL, last_seen_build TEXT NOT NULL,
                    translation_version TEXT NOT NULL, notes TEXT NOT NULL,
                    suggestion TEXT, protected_status TEXT);
                CREATE TABLE audit(id INTEGER PRIMARY KEY, key TEXT, old_en TEXT, new_en TEXT,
                    old_sk TEXT, new_sk TEXT, old_status TEXT, new_status TEXT,
                    origin TEXT, build TEXT, translation_version TEXT, timestamp TEXT, reason TEXT);
                CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            ''')
        if self.db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('Corrupt Translation Memory')
        try:
            for row in self.rows().values():
                if row['source_hash'] != digest(row['source_en']) or row['status'] not in STATES:
                    raise ValueError('Invalid Translation Memory row: '+row['key'])
        except Exception:
            self.db.close();raise

    def rows(self):
        return {r['key']:dict(r) for r in self.db.execute('SELECT * FROM entries')}

    def meta(self, key):
        row = self.db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
        return row[0] if row else None

    def set_meta(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',(key,str(value)))

    def checkpoint(self):
        directory = self.work/'checkpoints'; directory.mkdir(exist_ok=True)
        path = directory/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex+'.sqlite3')
        backup = sqlite3.connect(path)
        try: self.db.backup(backup)
        finally: backup.close()
        if (self.work/'glossary.json').exists(): shutil.copy2(self.work/'glossary.json',path.with_suffix('.glossary.json'))
        return path

    def put(self, row, reason, old=None):
        if row['status'] not in STATES: raise ValueError('Unknown status')
        keys = list(row)
        self.db.execute('INSERT OR REPLACE INTO entries ('+','.join(keys)+') VALUES ('+','.join('?' for _ in keys)+')',[row[k] for k in keys])
        old = old or {}
        self.db.execute('INSERT INTO audit(key,old_en,new_en,old_sk,new_sk,old_status,new_status,origin,build,translation_version,timestamp,reason) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
            (row['key'],old.get('source_en'),row['source_en'],old.get('translation_sk'),row['translation_sk'],old.get('status'),row['status'],row['origin'],row['last_seen_build'],row['translation_version'],now(),reason))

    def close(self): self.db.close()
