python3 - <<'PYEOF'
import json,io
d=json.load(open("/tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/replay/sh/1642.json"))
s=io.open(d['file_path'],encoding='utf-8').read()
assert s.count(d['old'])==1, s.count(d['old'])
s=s.replace(d['old'],d['new'])
io.open(d['file_path'],'w',encoding='utf-8').write(s)
print('edit ok')
PYEOF