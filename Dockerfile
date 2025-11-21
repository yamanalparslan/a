# 1. Python'un hafif bir sürümünü temel al
FROM python:3.11-slim

# 2. Konsol çıktılarını anlık görebilmek için ayar
ENV PYTHONUNBUFFERED=1

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Gerekli sistem kütüphanelerini yükle (PostgreSQL için)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Gereksinim dosyasını kopyala ve yükle
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Proje kodlarını kopyala
COPY . /app/

# 7. Konteyner çalıştığında bu komutu çalıştır (Sunucuyu başlat)
CMD ["gunicorn", "padel_community.wsgi:application", "--bind", "0.0.0.0:8000"]