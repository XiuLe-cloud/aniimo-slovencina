"""Resumable local English -> Slovak draft; no game files are modified."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.translation-deps'))
import ctranslate2
import sentencepiece

# Keep formatting, interpolation and the game's name byte-for-byte intact.
PROTECTED = re.compile(r'(<[^>\n]+>|\{[^{}]*\}|#[A-Za-z_][A-Za-z0-9_]*#|\$[A-Za-z_][A-Za-z0-9_]*|\[[A-Za-z_]+:[^\]\n]*\]|%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?[sdifouxXeEgGc%]|(?<![A-Za-z_])[-+]?\d+(?:[.,]\d+)*(?:%|‰)?|\\[nrt]|\r\n|\r|\n|[♪♫]|\bAniimo\b)')

def pieces(text):
    result = []
    for i, part in enumerate(PROTECTED.split(text)):
        if not part:
            continue
        if i % 2 or not re.search('[A-Za-z]', part):
            result.append((False, part))
        else:
            m = re.fullmatch(r'(\s*)(.*?)(\s*)', part, re.S)
            left, core, right = m.groups()
            if left: result.append((False, left))
            # Bound input lengths without dropping any content.
            # Translate sentences separately; this model can drop a second
            # sentence when fed several short sentences as a single input.
            chunks = re.split(r'((?<=[.!?])\s+(?=[A-Z]))', core)
            for chunk in chunks:
                if not chunk: continue
                if len(chunk) > 1000:
                    chunks2 = re.split(r'(\s+)', chunk)
                    acc = ''
                    for token in chunks2:
                        if len(acc) + len(token) > 700 and acc:
                            result.append((bool(re.search('[A-Za-z]', acc)), acc))
                            acc = ''
                        acc += token
                    if acc: result.append((bool(re.search('[A-Za-z]', acc)), acc))
                else:
                    result.append((bool(re.search('[A-Za-z]', chunk)), chunk))
            if right: result.append((False, right))
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args()
    source = [json.loads(line)['en'] for line in (ROOT/'source/unique-english.jsonl').read_text(encoding='utf-8-sig').splitlines()]
    manual = json.loads((ROOT/'translations.sk.json').read_text(encoding='utf-8-sig'))
    plans = {text: pieces(text) for text in source if text not in manual}
    required = dict.fromkeys(part for parts in plans.values() for translate,part in parts if translate)
    cache_path = ROOT/'source/segment-cache.jsonl'
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text(encoding='utf-8').splitlines():
            row=json.loads(line); cache[row['en']]=row['sk'].replace('\u2581',' ').strip()
    pending = [s for s in required if s not in cache]
    pending.sort(key=len)
    if args.limit: pending=pending[:args.limit]
    model = ROOT/'.translation-model/translate-en_sk-1_9'
    sp=sentencepiece.SentencePieceProcessor(model_file=str(model/'sentencepiece.model'))
    translator=ctranslate2.Translator(str(model/'model'), device='cpu', compute_type='int8', inter_threads=1, intra_threads=args.threads)
    start=time.monotonic()
    print(json.dumps({'segments_total':len(required),'cached':len(cache),'pending':len(pending),'cpu_count':os.cpu_count()}),flush=True)
    with cache_path.open('a',encoding='utf-8') as out:
        for offset in range(0,len(pending),32):
            batch=pending[offset:offset+32]
            tokens=[sp.encode(s,out_type=str) for s in batch]
            translations=translator.translate_batch(tokens,beam_size=2,max_batch_size=32,max_input_length=0,max_decoding_length=768,repetition_penalty=1.1)
            for en,translated in zip(batch,translations):
                sk=sp.decode(translated.hypotheses[0]).replace('\u2581',' ').strip()
                if not sk:
                    retry=translator.translate_batch([sp.encode(en.replace('\ufffd',''),out_type=str)],beam_size=4,max_input_length=0,max_decoding_length=768)
                    sk=sp.decode(retry[0].hypotheses[0]).replace('\u2581',' ').strip()
                if not sk:
                    # Preserve broken source fragments instead of deleting text.
                    sk=en
                    with (ROOT/'source/empty-translation-fallbacks.jsonl').open('a',encoding='utf-8') as problems:
                        problems.write(json.dumps({'en':en},ensure_ascii=False)+'\n')
                cache[en]=sk
                out.write(json.dumps({'en':en,'sk':sk},ensure_ascii=False)+'\n')
            out.flush()
            done=min(offset+32,len(pending))
            if done%256==0 or done==len(pending):
                status={'done':done,'pending_run':len(pending),'cached':len(cache),'segments_total':len(required),'seconds':round(time.monotonic()-start,1)}
                print(json.dumps(status),flush=True)
                (ROOT/'source/progress.json').write_text(json.dumps(status),encoding='utf-8')
    result={}
    incomplete=[]
    for text in source:
        if text in manual:
            result[text]=manual[text]
        elif all(not trans or part in cache for trans,part in plans[text]):
            result[text]=''.join(cache[part] if trans else part for trans,part in plans[text])
        else: incomplete.append(text)
    for en,sk in list(result.items()):
        for annotation in ['City name (optional, probably does not need a translation)','star name']:
            if annotation not in en: sk=sk.replace(annotation,'')
        if 'Nimbus Fields' in en: sk=sk.replace('Nimbus Fields','Nimbové pláne')
        result[en]=sk
    (ROOT/'translations.full.sk.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'source/translation-status.json').write_text(json.dumps({'total':len(source),'complete':len(result),'incomplete':len(incomplete),'method':'Argos en-sk 1.9, local machine translation + manual UI overrides','human_review':'partial'},indent=2),encoding='utf-8')
    print(f'Complete entries: {len(result)}/{len(source)}',flush=True)

if __name__=='__main__': main()
