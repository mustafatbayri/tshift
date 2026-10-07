cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor/cozucu && python3 - <<'EOF'
import io,re
p="coz.py"
s=io.open(p,encoding="utf-8").read()
# 1) kosul fonksiyonunu kaldir
a=s.index("def _fazla_mesai_kisayolu_gecerli(kuruldu):")
b=s.index("def _fazla_mesaiyi_sifirla(kuruldu):")
s=s[:a]+s[b:]
# 2) _sinir_kapsami
old='''    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("bulundu"):
        return "fazla_mesaisiz"'''
new='''    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):
        return "fazla_mesaisiz"'''
assert s.count(old)==1; s=s.replace(old,new)
# 3) VARSAYILAN: olcum anahtari
old='''    "fazla_mesai_once_sifir": True,
}'''
new='''    "fazla_mesai_once_sifir": True,
    "fazla_mesai_sifirda_tut": False,
}'''
assert s.count(old)==1; s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok", len(s))
EOF
grep -n "_fazla_mesai_kisayolu_gecerli\|uygulandi\|sifirda" coz.py | cut -c1-160