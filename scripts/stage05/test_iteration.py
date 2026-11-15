"""Demonstrate the controllable SVG/Inkscape half; Affinity acceptance is separate."""
from pathlib import Path
import json,hashlib,subprocess,copy,os
from xml.etree import ElementTree as E
R=Path(__file__).resolve().parents[2];D=R/'tests/stage05/iteration';LOG=R/'reports/stage05/logs';SVG='http://www.w3.org/2000/svg';INK='http://www.inkscape.org/namespaces/inkscape';SOD='http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
E.register_namespace('',SVG);E.register_namespace('inkscape',INK);E.register_namespace('sodipodi',SOD)
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def tag(x):return '{'+SVG+'}'+x
def render(phase):
 root=E.Element(tag('svg'),{'width':'2000','height':'480','viewBox':'0 0 2000 480'})
 nv=E.SubElement(root,'{'+SOD+'}namedview',{'id':'namedview'})
 defs=E.SubElement(root,tag('defs'));bg=E.parse(D/'background.svg').getroot().find('.//*[@id="background"]');bg.set('id','shared-background');defs.append(bg)
 for i,s in enumerate(['state_01','state_02','state_03']):
  x=i*680;E.SubElement(nv,'{'+INK+'}page',{'x':str(x),'y':'0','width':'640','height':'480','id':'page'+str(i+1)})
  g=E.SubElement(root,tag('g'),{'id':'board-'+str(i+1),'transform':f'translate({x},0)'})
  E.SubElement(g,tag('use'),{'href':'#shared-background'})
  g.append(E.parse(D/(s+'.svg')).getroot().find('.//*[@id="geometry"]'))
 out=D/('three_boards_'+phase+'.svg');E.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True)
 app=os.environ.get('SF_INKSCAPE','/Applications/Inkscape.app/Contents/MacOS/inkscape')
 for ext in ['png','pdf']:
  cmd=[app,str(out.relative_to(R)),'--export-page=all','--export-filename='+str((D/('three_boards_'+phase+'.'+ext)).relative_to(R))]
  run=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=90)
  (LOG/('iteration_'+phase+'_'+ext+'.json')).write_text(json.dumps({'command':cmd,'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr},ensure_ascii=False,indent=2)+'\n')
  assert run.returncode==0
 return root
# Reproducible reset from preserved BEFORE input.
(D/'state_02.svg').write_bytes((D/'state_02_before.svg').read_bytes())
before={s:h(D/(s+'.svg')) for s in ['state_01','state_02','state_03']};bg=h(D/'background.svg');a=render('before')
(D/'state_02.svg').write_bytes((D/'state_02_after.svg').read_bytes());b=render('after')
after={s:h(D/(s+'.svg')) for s in before}
result={'shared_background_sha256':bg,'before_hashes':before,'after_hashes':after,'state01_and_03_unchanged':all(before[s]==after[s] for s in ['state_01','state_03']),'state02_changed':before['state_02']!=after['state_02'],'background_unchanged':bg==h(D/'background.svg'),'board01_and_03_subtrees_unchanged':all(E.tostring(a.find('.//*[@id="board-'+str(i)+'"]'))==E.tostring(b.find('.//*[@id="board-'+str(i)+'"]')) for i in [1,3]),'scope':'parameter → separate SVG state → Inkscape multi-page PNG and PDF; Affinity evidence in reports/stage05/REVIEW.md'}
assert result['state01_and_03_unchanged'] and result['state02_changed'] and result['background_unchanged'] and result['board01_and_03_subtrees_unchanged']
(R/'reports/stage05/ITERATION_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
