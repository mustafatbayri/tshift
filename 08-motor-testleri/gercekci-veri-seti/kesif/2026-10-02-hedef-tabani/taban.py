# KESIF betigi (depo disi): hedef eksiginin kural merdiveni tabani.
import json,sys,os,time

from ortools.sat.python import cp_model
F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','fikstur','_sahne-S30-95.json')
s=json.load(open(F,encoding='utf-8'))
SEV=int(sys.argv[1]); AMAC=sys.argv[2]; SN=int(sys.argv[3]) if len(sys.argv)>3 else 120
T={t['id']:t for t in s['vardiya_sablonlari']}
def net_dk(t): return int(round((t['bit']-t['bas'])*60))-sum(m['dakika']*m['adet'] for m in t['mola_politikasi'])
dep={e:d for d in s['departmanlar'] for e in d['ekipler']}
def acik(t,g):
    a=dep[t['ekip']]['acik']
    if a=='7/24': return True
    return any(g in p['gunler'] and p['bas']<=t['bas'] and t['bit']<=p['bit'] for p in a)
m=cp_model.CpModel(); x={}
cal=[c for c in s['calisanlar'] if c.get('durum','aktif')=='aktif']
for c in cal:
    izin={i['gun'] for i in c['izinler'] if i.get('durum','onayli')=='onayli'}
    uyg={u['gun'] for u in c['uygunluk'] if u['tip']=='uygun_degil' and u['bas']==0 and u['bit']==24} if SEV>=1 else set()
    for g in range(7):
        if g in izin or g in uyg: continue
        for t in T.values():
            if t['ekip'] not in c['ekipler']: continue
            if 'gunler' in t and g not in t['gunler']: continue
            if not acik(t,g): continue
            if SEV>=1 and c.get('gece_calisamaz') and t.get('gece_vardiyasi'): continue
            x[c['id'],g,t['id']]=m.NewBoolVar('')
fm=[]
for c in cal:
    v=[(g,t) for (ci,g,t) in x if ci==c['id']]
    for g in range(7): m.Add(sum(x[c['id'],g,t] for (gg,t) in v if gg==g)<=1)
    m.Add(sum(x[c['id'],g,t] for g,t in v)<=6)
    net=sum(net_dk(T[t])*x[c['id'],g,t] for g,t in v)
    soz=c['sozlesme']; hs=soz.get('haftalik_saat')
    if soz['tip']=='yari_zamanli' or hs is None:
        m.Add(net<=45*60); continue
    if soz['tip']=='tam_zamanli':
        gs=soz.get('gun_sayisi') or 6
        iz=len({i['gun'] for i in c['izinler'] if i.get('durum','onayli')=='onayli'})
        m.Add(net>=max(0,int(round((hs-iz*hs/gs)*60))))
    f=m.NewIntVar(0,600,''); m.Add(f>=net-hs*60); fm.append(f)
    if SEV>=2:
        for g in range(6):
            for (g1,t1) in v:
                if g1!=g: continue
                for (g2,t2) in v:
                    if g2==g+1 and (24+T[t2]['bas'])-T[t1]['bit']<11: m.AddImplication(x[c['id'],g,t1],x[c['id'],g2,t2].Not())
    if SEV>=3:
        for g in range(4):
            m.Add(sum(x[c['id'],gg,t] for (gg,t) in v if g<=gg<=g+3 and T[t].get('gece_vardiyasi'))<=3)
eks=[];asm=[];ekip_eks={}
for h in s['talep']:
    an=h['gun']*24+h['saat']
    cov=sum(var for (ci,g,t),var in x.items() if T[t]['ekip']==h['ekip'] and g*24+T[t]['bas']<=an<g*24+T[t]['bit'])
    m.Add(cov>=h.get('asgari',0))
    d=m.NewIntVar(0,h['hedef'],''); m.Add(d>=h['hedef']-cov); eks.append(d)
    a=m.NewIntVar(0,500,''); m.Add(a>=cov-h['hedef']); asm.append(a)
    ekip_eks.setdefault(h['ekip'],[]).append(d)
E_,FM,A=sum(eks),sum(fm),sum(asm)
if AMAC=='eksik_fm0': m.Add(FM==0); m.Minimize(E_)
elif AMAC=='eksik': m.Minimize(E_)
elif AMAC=='urun': m.Minimize(9*E_+50*FM)       # 9/kisi-saat, 50/dakika
elif AMAC=='fm': m.Minimize(FM)
sol=cp_model.CpSolver(); sol.parameters.max_time_in_seconds=SN; sol.parameters.num_workers=2
t0=time.time(); r=sol.Solve(m)
print('sev',SEV,'amac',AMAC,sol.StatusName(r),'%.0fsn'%(time.time()-t0),'amac=%s alt_sinir=%s'%(sol.ObjectiveValue(),sol.BestObjectiveBound()) if r in(cp_model.OPTIMAL,cp_model.FEASIBLE) else '')
if r in(cp_model.OPTIMAL,cp_model.FEASIBLE):
    print('  eksik kisi-saat',sol.Value(E_),{e:sum(sol.Value(d) for d in v) for e,v in ekip_eks.items()},'fazla mesai saat',sol.Value(FM)/60,'asim',sol.Value(A))
