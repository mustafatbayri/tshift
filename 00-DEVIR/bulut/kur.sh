#!/usr/bin/env bash
# TShift bulut olcum makinesi -- KURULUM (Ubuntu 24.04, Hetzner CCX43/CCX53)
# Kullanim (Mustafa'nin PC'sinden):
#   ssh -i %USERPROFILE%\.ssh\tshift_bulut root@<IP> "bash -s" -- < 00-DEVIR\bulut\kur.sh <TOKEN>
# <TOKEN>: GitHub salt okunur (Contents: Read) belirteci; yalniz bu makinede durur.
# Rehber: 00-DEVIR/BULUT-OLCUM-MAKINESI.md
set -euo pipefail
TOKEN="${1:?GitHub salt okunur belirteci gerekli (bkz. rehber §2)}"
export DEBIAN_FRONTEND=noninteractive
echo "== $(date '+%F %T')  paketler"
apt-get update -qq && apt-get install -y -qq git python3 python3-venv python3-pip > /dev/null
echo "== $(date '+%F %T')  depo -> /opt/tshift"
if [ -d /opt/tshift/.git ]; then
  git -C /opt/tshift pull --ff-only -q
else
  git clone -q "https://x-access-token:${TOKEN}@github.com/mustafatbayri/tshift.git" /opt/tshift
fi
git -C /opt/tshift remote set-url origin "https://github.com/mustafatbayri/tshift.git"   # belirtec .git/config'de KALMAZ
git -C /opt/tshift config user.name "tshift-bulut (commit YAPMAZ)"
echo "== $(date '+%F %T')  python ortami"
python3 -m venv /opt/venv
/opt/venv/bin/pip install -q --upgrade pip
/opt/venv/bin/pip install -q -r /opt/tshift/09-motor/requirements.txt
mkdir -p /opt/sonuc
echo "== $(date '+%F %T')  makine: $(hostname), $(nproc) mantiksal cekirdek, $(free -g | awk '/Mem:/{print $2}') GB"
/opt/venv/bin/python -c "import ortools, sys; print('ortools', ortools.__version__, 'python', sys.version.split()[0])"
echo "== $(date '+%F %T')  testler (yesil degilse OLCUM BASLAMAZ)"
cd /opt/tshift/09-motor && /opt/venv/bin/python -m pytest testler -q -p no:cacheprovider | tail -n 2
cd /opt/tshift/08-motor-testleri/gercekci-veri-seti && /opt/venv/bin/python -m pytest testler -q -p no:cacheprovider | tail -n 2
cd /opt/tshift/10-veri-seti/v2 && /opt/venv/bin/python -m pytest testler -q -p no:cacheprovider | tail -n 2
echo "== $(date '+%F %T')  KURULUM BITTI -- blok: nohup bash /opt/tshift/00-DEVIR/bulut/blok.sh > /opt/blok.log 2>&1 &"
