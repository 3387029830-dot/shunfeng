"""Stage0.5 neutral software integration; does not draw production assets."""
from pathlib import Path
import subprocess,json,hashlib,re,copy,sys,os,unicodedata
from xml.etree import ElementTree as ET
from pypdf import PdfReader
from pypdf.generic import ContentStream
ROOT=Path(__file__).resolve().parents[2]
APP=os.environ.get('SF_INKSCAPE','/Applications/Inkscape.app/Contents/MacOS/inkscape')
BASE=ROOT/'tests/stage05';OUT=BASE/'inkscape';LOG=ROOT/'reports/stage05/logs';NS={'s':'http://www.w3.org/2000/svg'}
OUT.mkdir(exist_ok=True,parents=True);LOG.mkdir(exist_ok=True,parents=True);records=[];tests=[]
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def run(args,label):
 cmd=[APP,*map(str,args)];r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=90)
 rec={'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 raw=json.dumps(rec,ensure_ascii=False,indent=2).replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${USER_HOME}')
 (LOG/(label+'.json')).write_text(raw+'\n');records.append(label)
 if r.returncode:raise RuntimeError(label+': '+r.stderr[:300])
 return r.stdout

def test(name,ok,detail):tests.append({'test':name,'status':'PASS' if ok else 'FAIL','detail':detail})
def export(inp,name,ext,extra=()):
 target=OUT/(name+'.'+ext);run([rel(inp),'--export-area-page',*extra,'--export-filename='+rel(target)],name+'_'+ext);return target
inp=BASE/'inputs/neutral.svg';original_hash=h(inp)
run(['--version'],'version')
roundtrip=export(inp,'neutral_inkscape','svg')
a=ET.parse(inp).getroot();b=ET.parse(roundtrip).getroot()
ids=lambda root:{n.get('id'):n for n in root.iter() if n.get('id')}
A,B=ids(a),ids(b)
test('import_groups',all(x in B for x in ['layer-base','layer-shapes','level-2','level-3','layer-text']),'SVG groups and IDs retained after Inkscape parse/export')
test('nested_groups',b.find('.//s:g/s:g/s:g',NS) is not None,'three nested g elements')
test('live_chinese_svg',''.join(B['chinese'].itertext())==''.join(A['chinese'].itertext()),'editable text node retained')
test('opacity',B['rectangle'].get('opacity')=='0.55' or 'opacity:0.55' in B['rectangle'].get('style',''),'55% opacity')
test('clip',bool(B['clipped'].get('clip-path')) or 'clip-path:' in B['clipped'].get('style',''),'clip relation retained')
modified=OUT/'neutral_node_modified.svg'
run([rel(roundtrip),'--select=bezier','--actions=object-set-attribute:d,M 60 360 C 180 250 230 420 350 330;export-filename:'+rel(modified)+';export-do'],'node_edit')
C=ids(ET.parse(modified).getroot());nums=lambda s:[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',s)]
test('path_control_point_edit',nums(C['bezier'].get('d'))==[60,360,180,250,230,420,350,330],'Bezier first control point y:270→250 using Inkscape object action')
test('isolated_element_edit',all(ET.tostring(B[x])==ET.tostring(C[x]) for x in ['circle','rectangle','clipped','chinese']),'other named primitives and text unchanged after node edit')
png1=export(inp,'neutral','png');png2=export(inp,'neutral_repeat','png')
test('repeat_png_stable',h(png1)==h(png2),'SHA256 equal')
pdf=export(inp,'neutral_live','pdf');pdf2=export(inp,'neutral_live_repeat','pdf');outline=export(inp,'neutral_outlined','pdf',['--export-text-to-path'])
def analyze_pdf(f):
 r=PdfReader(str(f));p=r.pages[0];ops=ContentStream(p.get_contents(),r).operations
 fonts=p['/Resources'].get('/Font',{})
 return {'pages':len(r.pages),'page_pt':[float(x) for x in p.mediabox],'images':len(p.images),'path_operations':sum(op in [b'm',b'l',b'c',b're'] for _,op in ops),'clip_operations':sum(op in [b'W',b'W*'] for _,op in ops),'text':p.extract_text(),'fonts':[{'name':str(x.get_object().get('/BaseFont')),'subtype':str(x.get_object().get('/Subtype'))} for x in fonts.values()],'content_sha256':hashlib.sha256(p.get_contents().get_data()).hexdigest()}
p,q,o=analyze_pdf(pdf),analyze_pdf(pdf2),analyze_pdf(outline)
test('vector_pdf',p['images']==0 and p['path_operations']>0,p)
test('chinese_live_pdf_exact_unicode','中文测试' in p['text'],{'raw_text':p['text'],'issue':'font ToUnicode maps 文 to Kangxi radical ⽂; retain this exact extraction failure'})
test('chinese_live_pdf_nfkc','中文测试' in unicodedata.normalize('NFKC',p['text']),unicodedata.normalize('NFKC',p['text']))
test('outlined_vector_pdf',o['images']==0 and o['path_operations']>p['path_operations'],o)
test('repeat_pdf_page_content_stable',p['content_sha256']==q['content_sha256'],'page content hash, excludes volatile PDF metadata')
for s in ['state_01','state_02','state_03']:
 export(BASE/'inputs'/(s+'.svg'),s,'png');export(BASE/'inputs'/(s+'.svg'),s,'pdf')
test('batch_export',all((OUT/(s+'.'+ext)).exists() for s in ['state_01','state_02','state_03'] for ext in ['png','pdf']),'3 states × PNG/PDF')
test('input_unchanged',h(inp)==original_hash,original_hash)
# Separate shared background and per-state foreground assets for the real GUI link test.
sys.path.insert(0,str(ROOT/'scripts'));from geometry import geometry,save,root
c=json.loads((BASE/'inputs/geometry_test.json').read_text());dest=BASE/'iteration';dest.mkdir(exist_ok=True)
r=geometry(c,'state_01');bg=r.find('.//*[@id="background"]');r.remove(r.find('.//*[@id="geometry"]'));save(r,dest/'background.svg')
for s in c['states']:
 r=geometry(c,s);r.remove(r.find('.//*[@id="background"]'));save(r,dest/(s+'.svg'))
before={s:h(dest/(s+'.svg')) for s in c['states']};background_before=h(dest/'background.svg')
(dest/'state_02_before.svg').write_bytes((dest/'state_02.svg').read_bytes());c['states']['state_02']+=7
r=geometry(c,'state_02');r.remove(r.find('.//*[@id="background"]'));save(r,dest/'state_02_after.svg')
# Stable state_02.svg stays at BEFORE until the GUI placement is established. update script performs swap.
iteration={'before_hashes':before,'background_hash':background_before,'after_state02_hash':h(dest/'state_02_after.svg'),'only_state02_changes':h(dest/'state_01.svg')==before['state_01'] and h(dest/'state_03.svg')==before['state_03'] and h(dest/'background.svg')==background_before,'update_pending_gui':True}
test('shared_asset_isolation',iteration['only_state02_changes'] and before['state_02']!=iteration['after_state02_hash'],iteration)
report={'inkscape':run(['--version'],'version_final').strip(),'tests':tests,'logs':records,'pdf_metadata_bytes_equal':h(pdf)==h(pdf2),'iteration':iteration,'scope':'CLI/import/parse/export proof; GUI/manual edit and Affinity assessed separately'}
(ROOT/'reports/stage05/INKSCAPE_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':len(tests),'failed':[x['test'] for x in tests if x['status']!='PASS'],'version':report['inkscape']},ensure_ascii=False))
