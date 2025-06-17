#!/bin/bash
set -e

# Définir FLASK_APP pour que flask db fonctionne
export FLASK_APP=src/app.py

# Appliquer les migrations Alembic/Flask-Migrate
flask db upgrade

# Lancer l'application (adapté pour correspondre à la commande Dockerfile)
exec python src/app.py
