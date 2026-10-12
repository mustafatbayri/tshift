# -*- coding: utf-8 -*-
"""D'nin kurulum bedeli: tam olcek sahnesinde (fikstur/_sahne-S30-95.json) model
kisit/degisken sayisi ve kurma suresi. Kullanim: py kisit_say.py <09-motor klasoru>
(eski kodla kiyas icin eski bir kopyanin 09-motor'u verilir)."""
import io, json, os, sys, time
motor = os.path.abspath(sys.argv[1]); sys.path.insert(0, motor)
from cozucu.model import Model
BURASI = os.path.dirname(os.path.abspath(__file__))
g = json.load(io.open(os.path.join(BURASI, "..", "..", "fikstur", "_sahne-S30-95.json"), encoding="utf-8"))
t = time.time(); k = Model(g).kur(); s = time.time() - t
p = k.m.Proto()
ro = [v for v in p.variables if v.name.startswith("ro_")]
print("%s: degisken %d, kisit %d, ro_ degiskeni %d, kurma %.1f sn" % (motor, len(p.variables), len(p.constraints), len(ro), s))
