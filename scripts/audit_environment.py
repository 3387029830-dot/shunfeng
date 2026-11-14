from pathlib import Path
import subprocess, json, datetime, os, shutil
p=Path(__file__).resolve().parents[1]/'reports'
commands=[['uname','-m'],['sw_vers'],['sysctl','-n','hw.memsize'],['python3','--version'],['git','--version'],['/usr/libexec/PlistBuddy','-c','Print :CFBundleShortVersionString','/Applications/Google Chrome.app/Contents/Info.plist']]
results=[]
for c in commands:
 r=subprocess.run(c,capture_output=True,text=True);results.append({'command':c,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
r=subprocess.run(['system_profiler','SPHardwareDataType'],capture_output=True,text=True)
results.append({'command':['system_profiler','SPHardwareDataType','(filtered)'],'exit':r.returncode,'stdout':'\n'.join(x for x in r.stdout.splitlines() if any(y in x for y in ['Model Name:','Model Identifier:','Chip:','Memory:'])),'stderr':r.stderr})
apps=[]; roots=['/Applications','/System/Applications',str(Path.home()/'Applications')]
for base in roots:
 if not Path(base).exists(): continue
 for root,dirs,files in os.walk(base):
  if len(Path(root).relative_to(base).parts)>3: dirs[:]=[];continue
  for d in dirs:
   if any(x in d.lower() for x in ['inkscape','affinity','blender']): apps.append(str(Path(root)/d))
  dirs[:]=[d for d in dirs if not d.endswith('.app')]
report={'client_date':'2026-11-14','timezone':'Asia/Shanghai','scope':'local host via shell; standard application folders, max depth 4; not every mounted disk/custom folder','commands':results,'target_apps':apps,'searched_roots':roots,'path_executables':{x:shutil.which(x) for x in ['inkscape','blender']}}
(p/'environment_current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2).replace(str(Path.home()),'${USER_HOME}')+'\n')
