"""Create a data-only release ZIP and its version.json. Never executes downloaded code."""
import argparse, hashlib, json, zipfile
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--package',default='dist/Aniimo-SK-3616231-strojovy-preklad')
p.add_argument('--output',default='dist/online')
p.add_argument('--base-url',required=True)
p.add_argument('--change',action='append',default=[])
a=p.parse_args();root=Path(a.package);m=json.loads((root/'manifest.json').read_text(encoding='utf-8-sig'))
version=str(m['translationVersion']);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
name=f'Aniimo-Slovencina-{version}.zip';target=out/name
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    z.writestr('manifest.json',json.dumps(m,ensure_ascii=False,indent=2))
    for file,expected in m['payloadFiles'].items():
        data=(root/'data'/file).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
        z.writestr('data/'+file,data)
feed={'translation_version':version,'game_build':str(m['gameBuild']),'package_url':a.base_url.rstrip('/')+'/'+name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'changelog':a.change}
(out/'version.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(feed,ensure_ascii=False,indent=2))
