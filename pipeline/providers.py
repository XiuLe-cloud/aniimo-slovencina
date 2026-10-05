"""Replaceable providers. Italian text is never sent to a translation provider."""
import json
import os
import re
import subprocess
from .data import unique_object
from .qa import TOKEN, glossary_terms

class Provider:
    def __init__(self, config, root): self.config=config; self.root=root; self.calls=[]

    def translate(self,key,en,glossary):
        self.calls.append(key)
        kind=self.config.get('type','disabled')
        terms=glossary_terms(glossary,key,en)
        # A generic local command adapter permits any provider/model without embedding credentials.
        if kind=='command':
            request={'task':'translate_en_to_sk','key':key,'source_en':en,'glossary':terms,
                     'instructions':'Use natural Slovak. EN is authoritative. Preserve full meaning, numbers, percent, tokens, markup, escapes and newlines. Return JSON {"translation_sk":"..."}. No Italian source.'}
            result=subprocess.run(self.config['argv'],input=json.dumps(request,ensure_ascii=False),text=True,
                encoding='utf-8',capture_output=True,timeout=self.config.get('timeout',120),cwd=self.root,check=False)
            if result.returncode: raise RuntimeError('AI provider failed (stderr withheld; may contain secrets)')
            data=json.loads(result.stdout,object_pairs_hook=unique_object)
            out=data['translation_sk']
        elif kind=='local':
            # Reuse the existing local model and sentence segmentation, without its bulk main().
            import translate_all as t
            if not hasattr(self,'engine'):
                model=self.root/'.translation-model/translate-en_sk-1_9'
                self.sp=t.sentencepiece.SentencePieceProcessor(model_file=str(model/'sentencepiece.model'))
                self.engine=t.ctranslate2.Translator(str(model/'model'),device='cpu',compute_type='int8',intra_threads=4)
            # Freeze glossary substitutions before sentence translation.
            alternatives=sorted((x['en_term'] for x in terms),key=len,reverse=True)
            pattern=re.compile(r'(?<!\w)('+ '|'.join(re.escape(x) for x in alternatives)+r')(?!\w)',re.I) if alternatives else None
            lookup={x['en_term'].casefold():x for x in terms}
            chunks=pattern.split(en) if pattern else [en]; out=''
            for chunk in chunks:
                term=lookup.get(chunk.casefold())
                if term:
                    out+=chunk if term['do_not_translate'] else term['preferred_sk_term']; continue
                # New special tokens not handled by legacy pieces are frozen first.
                for piece in re.split('('+TOKEN.pattern+')',chunk):
                    if not piece: continue
                    if TOKEN.fullmatch(piece): out+=piece; continue
                    for trans,part in t.pieces(piece):
                        if not trans: out+=part; continue
                        r=self.engine.translate_batch([self.sp.encode(part,out_type=str)],beam_size=2,max_input_length=0,max_decoding_length=1024)
                        translated=self.sp.decode(r[0].hypotheses[0]).replace('\u2581',' ').strip()
                        if not translated: raise RuntimeError('Empty AI output')
                        out+=translated
        else: raise RuntimeError('AI provider is disabled. Configure local or command provider.')
        if not isinstance(out,str) or not out.strip(): raise RuntimeError('Invalid AI output')
        return out

    def review(self, row):
        argv=self.config.get('semantic_argv')
        if not argv: return None
        request={'task':'semantic_review','item':row,'instructions':
            'EN authoritative, IT secondary. Compare meaning, omitted conditions/sentences, gameplay mechanics and natural Slovak. Never modify input. Return JSON {problem, suggested_sk, confidence} or {problem:null}.'}
        p=subprocess.run(argv,input=json.dumps(request,ensure_ascii=False),text=True,encoding='utf-8',
            capture_output=True,timeout=self.config.get('timeout',120),cwd=self.root,check=False)
        if p.returncode: raise RuntimeError('Semantic provider failed')
        d=json.loads(p.stdout,object_pairs_hook=unique_object)
        if not d.get('problem'): return None
        if d.get('confidence') not in {'HIGH','MEDIUM','LOW'} or not isinstance(d.get('suggested_sk'),str):
            raise ValueError('Invalid semantic response')
        return d
