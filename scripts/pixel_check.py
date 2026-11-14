from PIL import Image,ImageChops,ImageDraw
from pathlib import Path
import json
p=Path(__file__).resolve().parents[1];a=Image.open(p/'previews/neutral.png').convert('RGB');b=Image.open(p/'previews/neutral_patched.png').convert('RGB')
box=ImageChops.difference(a,b).getbbox()
states=[Image.open(p/f'previews/state_0{i}.png').convert('RGB') for i in [1,2,3]]
board=Image.new('RGB',(960,270),'white');d=ImageDraw.Draw(board)
for i,im in enumerate(states):
 board.paste(im.resize((320,240)),(i*320,30)); d.text((i*320+10,8),f'NEUTRAL GEOMETRY STATE {i+1}',fill='black')
board.save(p/'previews/geometry_contact.png')
result={'neutral_patch_pixel_bbox':box,'scope':'Only curve region changed visually; bbox in rendered pixels','opacity_sample_rgb':a.getpixel((333,267)),'clip_outside_rgb':a.getpixel((567,253)),'background_rgb':a.getpixel((10,10)),'png_size':list(a.size),'visual_review':'Chinese text legible; circle/rectangle/Bezier/clipping/opacity visible. Human-clock readability NOT evaluated.'}
(p/'reports/pixel_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(result)
