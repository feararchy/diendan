#!/bin/bash

echo "===================================="
echo " KINGMATE TECH FORUM - LINUX SETUP"
echo "===================================="

echo "Dang tao moi truong ao .venv..."
python3 -m venv .venv

echo "Dang kich hoat moi truong ao..."
source .venv/bin/activate

echo "Dang cap nhat pip..."
python -m pip install --upgrade pip

echo "Dang cai thu vien..."
pip install -r requirements.txt

echo "Dang tao migrations..."
python manage.py makemigrations

echo "Dang migrate database..."
python manage.py migrate

echo "===================================="
echo "Cai dat hoan tat."
echo "Neu chua co tai khoan admin, hay chay:"
echo "python manage.py createsuperuser"
echo "===================================="

echo "Dang chay server..."
python manage.py runserver 0.0.0.0:8000