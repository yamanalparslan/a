#!/usr/bin/env bash
# Hata olursa dur
set -o errexit

# Kütüphaneleri yükle
pip install -r requirements.txt

# Veritabanı tablolarını oluştur
python manage.py migrate

# CSS dosyalarını topla
python manage.py collectstatic --no-input