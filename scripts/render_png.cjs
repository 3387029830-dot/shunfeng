const fs = require('fs');
const path = require('path');
const sharp = require(process.env.SF_SHARP_MODULE || 'sharp');
const root=path.resolve(__dirname,'..');
(async()=>{
 const records=[];
 for(const f of fs.readdirSync(path.join(root,'tests/svg')).filter(x=>x.endsWith('.svg')).sort()) {
  const input=path.join(root,'tests/svg',f), output=path.join(root,'previews',f.replace('.svg','.png'));
  await sharp(input,{density:96}).png().toFile(output);
  const meta=await sharp(output).metadata(); records.push({input:f,output:path.basename(output),width:meta.width,height:meta.height,status:'PASS'});
 }
 fs.writeFileSync(path.join(root,'reports/render_results.json'),JSON.stringify({engine:'sharp/libvips SVG loader, not Inkscape',versions:sharp.versions,results:records},null,2)+'\n');
 console.log(JSON.stringify(records,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
