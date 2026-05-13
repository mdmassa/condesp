#!/bin/bash
set -e

echo "Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "Banco de dados pronto!"

echo "Aplicando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
