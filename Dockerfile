# Utiliser l'image officielle Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers de l'application
COPY . .

# Créer le répertoire pour la base de données
RUN mkdir -p /app/data

# Initialiser la base de données
RUN python init_db_approbation.py

# Exposer le port (Render utilise $PORT dynamiquement)
EXPOSE 10000

# Définir les variables d'environnement
ENV DATA_DIR=/opt/render/project/data
ENV PYTHONUNBUFFERED=1

# Commande de démarrage (utilise $PORT de Render)
CMD streamlit run app.py --server.port=${PORT:-10000} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false