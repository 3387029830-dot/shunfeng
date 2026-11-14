"""No installation, network, formal artwork or global configuration."""
import argparse,os,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--full',action='store_true');args=a.parse_args()
def run(cmd):
 subprocess.run(cmd,cwd=p,check=True)
run([sys.executable,'scripts/geometry.py'])
run([sys.executable,'scripts/test_structure.py'])
if args.full:
 run([os.environ.get('SF_NODE','node'),'scripts/render_png.cjs'])
 run([sys.executable,'scripts/pdf_diagnostic.py'])
 run(['sh','scripts/render_pdf_check.sh'])
 run([sys.executable,'scripts/pixel_check.py'])
