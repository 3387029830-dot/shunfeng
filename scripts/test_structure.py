import copy, hashlib, json, subprocess, sys
from pathlib import Path
from xml.etree import ElementTree as E
from geometry import ROOT, neutral, geometry, save, tag
out=ROOT/'tests/svg'; c=json.loads((ROOT/'config/geometry_test.json').read_text()); results=[]
def check(name,ok,detail):
 results.append({'test':name,'status':'PASS' if ok else 'FAIL','detail':detail})
def digest(b): return hashlib.sha256(b).hexdigest()
r=neutral(); ids=[n.get('id') for n in r.iter() if n.get('id')]
check('unique_ids',len(ids)==len(set(ids)),ids)
check('svg_structure',all(r.find('.//'+tag(n)) is not None for n in ['circle','rect','path','text','clipPath']), 'ElementTree parse + feature presence; not full SVG schema validation')
check('three_nested_groups',r.find('.//'+tag('g')+'/'+tag('g')+'/'+tag('g')) is not None,'g/g/g')
check('chinese_source',r.find('.//'+tag('text')).text=='中文测试：圆形、曲线、透明','Unicode text retained; not glyph rendering proof')
variants={s:geometry(c,s) for s in c['states']}
bgs=[E.tostring(x.find('.//*[@id="background"]')) for x in variants.values()]
check('shared_background',len(set(bgs))==1, digest(bgs[0]))
check('shared_center',all((x.find('.//*[@id="center"]').get('cx'),x.find('.//*[@id="center"]').get('cy'))==('320','280') for x in variants.values()), '320,280 for every state')
c2=copy.deepcopy(c);c2['states']['state_02']+=7
changed=[s for s in c['states'] if E.tostring(geometry(c,s))!=E.tostring(geometry(c2,s))]
check('isolated_parameter_update',changed==['state_02'],changed)
save(geometry(c2,'state_02'),out/'state_02_plus7.svg')
r2=copy.deepcopy(r);r2.find('.//*[@id="bezier"]').set('d','M 60 360 C 180 250 230 420 350 330')
changed=[a.get('id') for a,b in zip(r.iter(),r2.iter()) if a.attrib!=b.attrib or a.text!=b.text]
check('isolated_path_edit',changed==['bezier'],changed);save(r2,out/'neutral_patched.svg')
before={s:(out/(s+'.svg')).read_bytes() for s in c['states']}
subprocess.run([sys.executable,str(ROOT/'scripts/geometry.py')],check=True)
check('deterministic_rebuild',all((out/(s+'.svg')).read_bytes()==b for s,b in before.items()), {s:digest(b) for s,b in before.items()})
mtimes={s:(out/(s+'.svg')).stat().st_mtime_ns for s in c['states']}
subprocess.run([sys.executable,str(ROOT/'scripts/geometry.py'),'--state','state_02'],check=True)
check('targeted_export_no_other_write',all((out/(s+'.svg')).stat().st_mtime_ns==m for s,m in mtimes.items()), 'Content-aware writer; unchanged files keep mtime')
for f in sorted(out.glob('*.svg')):
 r=subprocess.run(['xmllint','--noout',str(f)],capture_output=True,text=True)
 check('xml_well_formed:'+f.name,r.returncode==0,r.stderr.strip())
(ROOT/'reports/structure_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
assert all(r['status']=='PASS' for r in results)
