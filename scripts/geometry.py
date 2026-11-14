"""Stage 0 only. No character, scene, or advertising drawing."""
import argparse, json, math
from pathlib import Path
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
E.register_namespace('',NS); E.register_namespace('inkscape',INK)
def tag(name): return '{'+NS+'}'+name
def sub(parent,name,**a): return E.SubElement(parent,tag(name),{k:str(v) for k,v in a.items()})
def root():
 return E.Element(tag('svg'),{'width':'640','height':'480','viewBox':'0 0 640 480','version':'1.1'})
def save(r,path):
 data=E.tostring(r,encoding='utf-8',xml_declaration=True)+b'\n'
 if not path.exists() or path.read_bytes()!=data: path.write_bytes(data)
 return data
def neutral():
 r=root();defs=sub(r,'defs');clip=sub(defs,'clipPath',id='clip');sub(clip,'circle',cx=490,cy=260,r=65)
 g=sub(r,'g',id='layer-base',**{'{'+INK+'}groupmode':'layer','{'+INK+'}label':'01 Base'})
 sub(g,'rect',x=0,y=0,width=640,height=480,fill='#f4f1ea')
 g=sub(r,'g',id='layer-shapes',**{'{'+INK+'}groupmode':'layer','{'+INK+'}label':'02 Shapes'})
 g=sub(g,'g',id='level-2');g=sub(g,'g',id='level-3')
 sub(g,'circle',id='circle',cx=120,cy=200,r=58,fill='#467b87')
 sub(g,'rect',id='rectangle',x=215,y=140,width=120,height=120,fill='#d58b65',opacity=.55)
 sub(g,'path',id='bezier',d='M 60 360 C 180 270 230 420 350 330',fill='none',stroke='#353c46',**{'stroke-width':8})
 sub(g,'rect',id='clipped',x=420,y=180,width=150,height=160,fill='#467b87',**{'clip-path':'url(#clip)'})
 g=sub(r,'g',id='layer-text',**{'{'+INK+'}groupmode':'layer','{'+INK+'}label':'03 Text'})
 sub(g,'text',id='chinese',x=38,y=68,fill='#353c46',**{'font-family':'Heiti SC, sans-serif','font-size':28}).text='中文测试：圆形、曲线、透明'
 return r
def geometry(c,state):
 r=root();g=sub(r,'g',id='background')
 sub(g,'rect',x=0,y=0,width=640,height=480,fill='#f4f1ea')
 sub(g,'rect',x=40,y=100,width=560,height=320,fill='none',stroke='#b9b9b9')
 sub(g,'circle',cx=c['center'][0],cy=c['center'][1],r=190,fill='none',stroke='#dddddd')
 g=sub(r,'g',id='geometry');x,y=c['center']
 for name,angle,length,color in [('variable',c['states'][state],c['lengths'][0],'#467b87'),('fixed',c['fixed_angle'],c['lengths'][1],'#353c46')]:
  rad=math.radians(angle)
  sub(g,'line',id=name,x1=x,y1=y,x2=f'{x+length*math.cos(rad):.6f}',y2=f'{y+length*math.sin(rad):.6f}',stroke=color,**{'stroke-width':12,'stroke-linecap':'round'})
 sub(g,'circle',id='center',cx=x,cy=y,r=9,fill='#d58b65')
 return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--state');args=a.parse_args()
 c=json.loads((ROOT/'config/geometry_test.json').read_text());out=ROOT/'tests/svg'
 if not args.state: save(neutral(),out/'neutral.svg')
 states=[args.state] if args.state else c['states']
 for s in states: save(geometry(c,s),out/(s+'.svg'))
