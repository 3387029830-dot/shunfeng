"""Scan tracked files only; report filenames/categories, never matched secrets."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','ls-files','-z'],cwd=p).decode().split('\0');paths=[x for x in paths if x]
patterns={'personal_home':rb'/(?:Users|home)/[A-Za-z0-9._-]+','github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})','private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','bearer_value':rb'(?i)authorization\s*[:=]\s*[\"\x27]?bearer\s+[A-Za-z0-9._-]{20,}','url_credential':rb'https?://[^\s/@:]+:[^\s/@]+@'}
issues=[];entries=[]
for name in paths:
 f=p/name;b=f.read_bytes();entries.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 for category,pat in patterns.items():
  if re.search(pat,b):issues.append({'path':name,'category':category})
 if len(b)>5*1024*1024:issues.append({'path':name,'category':'requires_binary_size_review_over_5MiB'})
required=['WORKFLOW_AUDIT.md','TOOL_COMPARISON.md','WORKFLOW_ARCHITECTURE.md','TEST_REPORT.md','AGENTS.md','ROADMAP.md','BLOCKERS.md','docs/REVIEW_HANDOFF.md']
for name in required:
 if name not in paths:issues.append({'path':name,'category':'required_file_missing'})
print(json.dumps({'tracked_files':len(entries),'total_bytes':sum(x['bytes'] for x in entries),'largest_bytes':max(x['bytes'] for x in entries),'issues':issues},ensure_ascii=False,indent=2))
sys.exit(bool(issues))
