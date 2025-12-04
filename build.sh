#!/usr/bin/env bash
# Hata olursa dur
set -o errexit

# Kütüphaneleri yükle
pip install -r requirements.txt

# Veritabanı tablolarını oluştur
python manage.py migrate

# Eski statik dosyaları temizle ve yenilerini topla (Jazzmin kalıntılarını siler)
python manage.py collectstatic --no-input --clear