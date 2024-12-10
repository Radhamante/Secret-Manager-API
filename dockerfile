# Étape 1 : Utiliser une image Python légère
FROM python:3.11-slim

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /api

# Étape 3 : Copier les fichiers de l'application
COPY requirements.txt /api/requirements.txt

# Étape 4 : Installer les dépendances
RUN pip install -r requirements.txt

# Étape 5 : Exposer le port utilisé par FastAPI (par défaut 8000)
EXPOSE 8081

# Étape 6 : Commande pour démarrer l'application
CMD ["python", "startServer.py"]
