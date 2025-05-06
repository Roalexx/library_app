#!/bin/sh

echo "Veritabanı migration başlatılıyor..."
flask db upgrade

echo "Flask uygulaması başlatılıyor..."
exec flask run --host=0.0.0.0 --port=5000

