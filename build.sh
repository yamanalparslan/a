#!/usr/bin/env bash
# Hata olursa dur
set -o errexit

# Kütüphaneleri yükle
pip install -r requirements.txt

# Eski statik dosyaları temizle ve yenilerini topla
python manage.py collectstatic --no-input --clear