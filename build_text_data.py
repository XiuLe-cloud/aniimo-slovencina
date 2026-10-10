"""Validate the editable snapshot and rebuild text payloads, without touching the game."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from pipeline.data import load_source, write_json
from pipeline.qa import check

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('dist/text-0.07'))
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    rows=json.loads((root/'data/translations.sk.json').read_text(encoding='utf8'))
    manifest=json.loads((root/'package/manifest.json').read_text(encoding='utf-8-sig'))
    glossary=json.loads((root/'data/glossary.json').read_text(encoding='utf8'))
    errors=[issue for key,row in rows.items() for issue in check(key,row['source'],row['translation'],glossary) if issue['severity']=='ERROR']
    if errors: raise ValueError(errors[:20])
    if len(rows)!=manifest['records']: raise ValueError('Record count differs')
    binary=bytearray(struct.pack('<I',manifest['textVersion']))
    mapping={'_version':manifest['textVersion'],'_count':len(rows)}
    cache={}
    for key,row in rows.items():
        text=row['translation']
        if text not in cache:
            raw=text.encode('utf8'); cache[text]=[len(binary),len(raw)]; binary.extend(raw)
        mapping[key]=cache[text]
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'Compress_en.bin').write_bytes(binary)
    write_json(args.output/'NewTextMap_en.json',mapping)
    actual,_=load_source(args.output)
    if actual!={k:v['translation'] for k,v in rows.items()}: raise ValueError('Roundtrip mismatch')
    for name in ('Compress_en.bin','NewTextMap_en.json'):
        digest=hashlib.sha256((args.output/name).read_bytes()).hexdigest()
        print(name,digest,'matches current manifest:',digest==manifest['payloadFiles'][name])
    print('Validated',len(rows),'records; zero blocking QA errors.')

if __name__=='__main__': main()
