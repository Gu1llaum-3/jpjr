#!/bin/bash
set -e

# Appliquer les migrations Alembic/Flask-Migrate
flask db upgrade

# Lancer l'application (adapté pour correspondre à la commande Dockerfile)
exec python src/app.py
