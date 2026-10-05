"""Conservative technical checks and optional reference triage, never rewriting text."""
import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path
from .data import digest, read_json
from build_package import TOKEN as LEGACY_TOKEN

TOKEN = re.compile(r'#c[0-9a-fA-F]{6}|#z|' + LEGACY_TOKEN.pattern + r'|#k[^\s#]+#z|\[[A-Za-z_]+:[A-Za-z0-9_]+\]|%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?[SD]|\\[abfv0\\]|&(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);')
NUM = re.compile(r'(?<![A-Za-z0-9_])\d+(?:[.,]\d+)*(?:\s*[%‰])?')
TAG = re.compile(r'<(/?)([A-Za-z][\w-]*)([^<>]*)>')
VOID = {'br','sprite','quad','space','page','pos','customrichtext','localizationidtag','daytime','bossrush'}

def markup_errors(text):
    stack = []; errors = []
    for m in TAG.finditer(text):
        close, name, attrs = m.groups(); name = name.lower()
        if name in VOID or attrs.rstrip().endswith('/'): continue
        if close:
            if not stack or stack.pop() != name: errors.append('unbalanced '+name)
        else: stack.append(name)
    if stack: errors.append('unclosed '+','.join(stack))
    return errors

def glossary_terms(glossary, key, en):
    return [t for t in glossary['terms'] if (not t.get('keys') or key in t['keys']) and
            re.search(r'(?<!\w)'+re.escape(t['en_term'])+r'(?!\w)',en,re.I)]

def validate_glossary(glossary):
    if glossary.get('schema')!=1 or not isinstance(glossary.get('terms'),list): raise ValueError('Invalid glossary schema')
    seen=set()
    for term in glossary['terms']:
        for key in ('en_term','preferred_sk_term','context','notes'):
            if not isinstance(term.get(key),str): raise ValueError('Invalid glossary field: '+key)
        for key in ('do_not_translate','manual_lock'):
            if type(term.get(key)) is not bool: raise ValueError('Invalid glossary flag')
        for key in ('keys','alternatives'):
            if not isinstance(term.get(key),list) or not all(isinstance(x,str) for x in term[key]): raise ValueError('Invalid glossary list')
        identity=(term['en_term'].casefold(),tuple(sorted(term['keys'])))
        if not term['en_term'] or identity in seen: raise ValueError('Empty/duplicate glossary term')
        if not term['do_not_translate'] and not term['preferred_sk_term']: raise ValueError('Empty preferred term')
        seen.add(identity)
    return glossary

def check(key, en, sk, glossary):
    issues = []
    def add(severity, code): issues.append({'key':key,'severity':severity,'code':code})
    if not isinstance(sk,str): add('ERROR','INVALID_TYPE'); return issues
    try: sk.encode('utf-8',errors='strict')
    except UnicodeError: add('ERROR','UTF8'); return issues
    if '\ufffd' in sk or '\u2581' in sk: add('ERROR','DAMAGED_ENCODING')
    if en.strip() and not sk.strip(): add('ERROR','EMPTY')
    if TOKEN.findall(en) != TOKEN.findall(sk): add('ERROR','TOKENS_OR_NEWLINES')
    if markup_errors(sk) and (not markup_errors(en) or TOKEN.findall(en)!=TOKEN.findall(sk)): add('ERROR','MARKUP')
    if markup_errors(en): add('WARNING','SOURCE_MARKUP')
    # Keep line boundaries: deleting them merges a preceding word with a numbered list.
    strip_token = lambda m: m.group() if m.group() in ('\n', '\r', '\r\n') else ''
    clean_en = TOKEN.sub(strip_token,en); clean_sk = TOKEN.sub(strip_token,sk)
    numbers = lambda text: Counter(re.sub(r'\s+','',n).replace(',','.') for n in NUM.findall(text))
    # EN thousands separators and Slovak grouped spaces represent the same value.
    clean_en_numbers = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', clean_en)
    clean_sk_numbers = re.sub(r'(?<=\d)[ \u00a0\u202f](?=\d{3}(?:\D|$))', '', clean_sk)
    for grouped in re.findall(r'\d{1,3}(?:,\d{3})+(?!\d)', clean_en):
        clean_sk_numbers = clean_sk_numbers.replace(grouped, grouped.replace(',', ''))
    if numbers(clean_en_numbers) != numbers(clean_sk_numbers): add('ERROR','NUMBERS_OR_PERCENT')
    if clean_en.count('%') != clean_sk.count('%'): add('ERROR','PERCENT')
    if len(clean_en)>30 and len(clean_sk)<len(clean_en)*.42: add('WARNING','TOO_SHORT')
    if len(clean_en)>10 and len(clean_sk)>len(clean_en)*2.5: add('WARNING','TOO_LONG')
    if clean_en==clean_sk and re.search(r'[A-Za-z]{4}',clean_en): add('WARNING','ENGLISH_OR_PROPER_NAME')
    if len(re.findall(r'[.!?](?:\s|$)',clean_en))>len(re.findall(r'[.!?](?:\s|$)',clean_sk))+1:
        add('WARNING','MISSING_SENTENCE_SEGMENTS')
    if unicodedata.normalize('NFC',sk)!=sk: add('WARNING','NON_NFC')
    if len(sk)>100 and re.search('[a-zA-Z]',sk) and not re.search('[áäčďéíĺľňóôŕšťúýžÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ]',sk):
        add('INFO','CHECK_SLOVAK_DIACRITICS')
    for term in glossary_terms(glossary,key,en):
        wanted = [term['en_term']] if term['do_not_translate'] else [term['preferred_sk_term']]+term['alternatives']
        if not any(re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',sk,re.I) for t in wanted):
            add('ERROR' if term['manual_lock'] else 'WARNING','GLOSSARY:'+term['en_term'])
    return issues

def profile(rows):
    counts=Counter(token for en in rows.values() for token in TOKEN.findall(en))
    # Retain unknown-looking forms so new engine syntax is visible instead of guessed.
    suspects=Counter(t for en in rows.values() for t in re.findall(r'#[^\s]+|\{[^\n]*?\}|%[A-Za-z]|\\.',en) if not TOKEN.fullmatch(t))
    return {'recognized':dict(counts),'unclassified_candidates':dict(suspects)}

def reference(config, build):
    try:
        if not config or not config.get('enabled'): return {}, 'REFERENCE_UNAVAILABLE: disabled'
        if config.get('license') != 'MIT' or not config.get('license_reviewed'):
            return {}, 'REFERENCE_UNAVAILABLE: license not reviewed'
        if str(build) != str(config['game_build']): return {}, 'REFERENCE_UNAVAILABLE: build mismatch'
        path=Path(config['csv'])
        if digest(path.read_bytes())!=config['sha256']: raise ValueError('reference hash mismatch')
        rows={}
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=['key','source_sha256','it']: raise ValueError('unknown reference format')
            for r in reader:
                if r['key'] in rows: raise ValueError('duplicate reference key')
                rows[r['key']]=r
        return rows, None
    except (OSError,ValueError,KeyError,csv.Error) as e:
        return {}, 'REFERENCE_UNAVAILABLE: '+str(e)

def semantic_row(key,en,sk,it,problems,suggestion=None,confidence='LOW'):
    return {'key':key,'en':en,'current_sk':sk,'it_reference':it,'status':'SEMANTIC_REVIEW',
            'problem':problems,'suggested_sk':suggestion,'confidence':confidence,'action':'MANUAL REVIEW REQUIRED'}

def cross_check(key,en,sk,ref,issues):
    r=ref.get(key)
    if not r or r['source_sha256']!=digest(en): return None
    # This is triage, not a claim of automatic semantic equivalence.
    relevant=[i['code'] for i in issues if i['severity']!='INFO']
    if len(en)>40 and len(r['it'])>len(sk)*2: relevant.append('SK_SHORTER_THAN_REFERENCE')
    if not relevant: return None
    return semantic_row(key,en,sk,r['it'],relevant)
