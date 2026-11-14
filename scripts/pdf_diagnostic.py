"""Raster transport diagnostic only; DOES NOT validate SVG-to-vector-PDF."""
from pathlib import Path
from reportlab.pdfgen import canvas
from pypdf import PdfReader
import json
r=Path(__file__).resolve().parents[1]
p=r/'tests/svg/raster_diagnostic.pdf'
c=canvas.Canvas(str(p),pagesize=(640,520),invariant=1)
c.setFont('Helvetica',12);c.drawString(20,497,'RASTER DIAGNOSTIC ONLY - not vector / not print-ready')
c.drawImage(str(r/'previews/neutral.png'),0,0,width=640,height=480)
c.save()
pdf=PdfReader(str(p));page=pdf.pages[0]
result={'status':'PASS (raster transport only)','pages':len(pdf.pages),'page_pt':list(page.mediabox),'image_count':len(page.images),'text':page.extract_text(),'limitations':'SVG paths, editable Chinese text, PDF/X, ICC and print reliability NOT tested'}
(r/'reports/pdf_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,indent=2))
