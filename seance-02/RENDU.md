
---

```markdown
# Rendu - Séance 2

**Nom et prénom :** KOMBATE GARIBA Moubarak  
**Identifiant GitHub :** Moubarak9096  
**Date de soumission :** 23/06/2026

---

## Résumé de la séance

Cette séance a été consacrée à la conteneurisation d'une application PySpark pour l'analyse du référentiel d'Anfa. J'ai écrit un Dockerfile pour créer une image personnalisée, construit l'image avec `docker build`, et mis en place les bonnes pratiques essentielles comme l'utilisation d'un `.dockerignore` et l'optimisation du cache Docker. J'ai ensuite orchestré une stack à 3 services (MinIO, Jupyter et mon image custom) avec Docker Compose. Enfin, j'ai exploré les données du bucket `anfa-raw` depuis un notebook Jupyter via les bibliothèques `boto3` et `pandas`.

---

## Étapes principales

1. Écriture du Dockerfile et construction de l'image `anfa-analyse:v1` (taille observée : 1.22 Go).
2. Mise en place du `.dockerignore` et observation du cache de Docker.
3. Écriture du `docker-compose.yml` orchestrant MinIO, Jupyter, et l'image custom.
4. Création du notebook `exploration_minio.ipynb` qui lit les données depuis MinIO via boto3 et pandas.

---

## Captures d'écran

### docker compose ps
seance-02/captures/docker-ps.png

### Notebook Jupyter

seance-02/captures/jupyter-pandas1.png

seance-02/captures/jupyter-pandas2.png


---

## Bonus multi-stage (optionnel)

J'ai comparé les tailles des images `anfa-analyse:v1` (sans multi-stage) et `anfa-analyse:v2-multistage` (avec multi-stage).

| Image | Taille | Différence |
| :--- | :--- | :--- |
| `anfa-analyse:v1` | 1.22 Go | Référence |
| `anfa-analyse:v2-multistage` | 1.22 Go | Aucune réduction significative |

**Analyse :**

La technique du multi-stage build permet normalement de réduire la taille d'une image Docker en éliminant les fichiers intermédiaires et les dépendances de compilation. Dans mon cas, les deux images ont la même taille (1.22 Go). Cela peut s'expliquer par les raisons suivantes :

- Les dépendances nécessaires à l'exécution (bibliothèques Python, Java, Spark) ont déjà une taille importante qui n'est pas réduite par le multi-stage.
- L'étape de compilation n'était pas très lourde, donc l'élimination des fichiers intermédiaires n'a pas eu d'impact significatif.
- Les couches Docker peuvent avoir été optimisées différemment, mais le résultat final reste équivalent.

Le multi-stage reste utile pour des projets plus complexes avec des compilations lourdes, mais pour ce cas d'usage (application Python avec Spark), l'avantage est minime.

![Comparaison des tailles v1 vs v2]seance-02/captures/image v1 vs taille image v2-multistage.png

---

## Réponses aux exercices d'application

### Exercice 1 : QCM conceptuel

**1.1** – **Réponse C** (Un conteneur partage le noyau de la machine hôte).  
*Justification* : Contrairement à une VM qui embarque son propre noyau, un conteneur Docker utilise le noyau de l'hôte via les namespaces et cgroups, ce qui le rend plus léger et plus rapide à démarrer.

**1.2** – **Réponse B** (L'image est un modèle figé en lecture seule ; le conteneur est une instance en cours d'exécution).  
*Justification* : L'image Docker est un template immuable contenant l'application et ses dépendances, tandis que le conteneur est une instance exécutable de cette image avec une couche d'écriture temporaire.

**1.3** – **Réponse B** (Les namespaces).  
*Justification* : Docker utilise les namespaces du noyau Linux pour isoler les espaces de noms (PID, réseau, utilisateur, montage, UTS, IPC) et ainsi créer un environnement isolé pour chaque conteneur.

**1.4** – **Réponse A** (Les cgroups).  
*Justification* : Les cgroups (control groups) permettent de limiter, prioriser et mesurer les ressources (CPU, mémoire, I/O) allouées à un conteneur.

**1.5** – **Réponse B** (Dans une machine virtuelle Linux invisible gérée par Docker Desktop).  
*Justification* : macOS n'étant pas basé sur le noyau Linux, Docker Desktop exécute un hyperviseur léger (HyperKit) qui fait tourner une VM Linux dédiée aux conteneurs.

**1.6** – **Réponse B** (La société d'origine qui a créé et open-sourcé Docker en 2013).  
*Justification* : DotCloud, une société de PaaS, a open-sourcé son outil de conteneurisation en 2013 sous le nom "Docker", révolutionnant ainsi l'écosystème des conteneurs.

**1.7** – **Réponse C** (Docker a apporté un format d'image portable, une CLI simple et un registre public).  
*Justification* : Docker s'appuie sur les primitives LXC/namespaces/cgroups mais a révolutionné l'écosystème avec l'image format standard (OCI), Docker Hub et une interface utilisateur simplifiée.

**1.8** – **Réponse B** (Open Container Initiative — une norme ouverte pour les images et le runtime).  
*Justification* : L'OCI est un projet sous la Linux Foundation qui standardise les formats d'images et les runtimes de conteneurs pour assurer l'interopérabilité entre les différents outils.

---

### Exercice 2 : Lecture et analyse d'un Dockerfile

#### 2.1 Explication de chaque instruction

| Instruction | Explication |
|-------------|-------------|
| `FROM python:3.11` | Définit l'image de base (Python 3.11 officiel) sur laquelle l'image sera construite. |
| `WORKDIR /application` | Définit le répertoire de travail à l'intérieur du conteneur pour toutes les instructions suivantes. |
| `COPY . /application` | Copie tous les fichiers du contexte de build (dossier local) dans le répertoire `/application` du conteneur. |
| `RUN pip install -r requirements.txt` | Exécute l'installation des dépendances Python listées dans le fichier `requirements.txt`. |
| `EXPOSE 5000` | Déclare que l'application écoute sur le port 5000 (à titre informatif, cela ne publie pas le port). |
| `CMD ["python", "main.py"]` | Définit la commande par défaut exécutée au lancement du conteneur (exécute `main.py` avec Python). |

#### 2.2 Différence entre `EXPOSE` et `-p`

| Élément | Description |
|---------|-------------|
| `EXPOSE 5000` | Déclare le port d'écoute dans le Dockerfile (documentation). Cela ne rend pas le port accessible depuis l'hôte. C'est une information pour l'utilisateur et pour certains orchestrateurs (ex: Docker Compose). |
| `-p 5000:5000` | Mappe le port 5000 du conteneur vers le port 5000 de l'hôte. **Sans cette option, le port n'est pas accessible depuis l'extérieur du conteneur.** |

#### 2.3 Deux problèmes et corrections

| # | Problème | Explication | Correction |
|---|----------|-------------|------------|
| 1 | **Cache non optimisé** | `COPY . /application` avant `RUN pip install` invalide le cache Docker à chaque modification de code, forçant la réinstallation des dépendances à chaque build, ce qui ralentit le processus de développement. | Déplacer `COPY requirements.txt /application/` avant `RUN pip install -r requirements.txt`, puis `COPY . .` après l'installation. |
| 2 | **Absence de `.dockerignore`** | Tous les fichiers du projet sont copiés (y compris les fichiers cachés, venv, .git, __pycache__, etc.) alourdissant l'image et exposant potentiellement des données sensibles. | Créer un fichier `.dockerignore` avec `__pycache__`, `*.pyc`, `.env`, `.git/`, `.dockerignore`, etc. |

#### 2.4 Version corrigée du Dockerfile

```dockerfile
# 1. Image de base plus légère
FROM python:3.11-slim

# 2. Définition du répertoire de travail
WORKDIR /app

# 3. Copie des dépendances AVANT le code (optimisation du cache)
COPY requirements.txt .

# 4. Installation des dépendances avec cache désactivé
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie du code source
COPY . .

# 6. Création d'un utilisateur non-root pour la sécurité
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# 7. Changement de propriétaire des fichiers
RUN chown -R appuser:appgroup /app

# 8. Passage à l'utilisateur non-root
USER appuser

# 9. Exposition du port
EXPOSE 5000

# 10. Commande de démarrage
CMD ["python", "main.py"]
```

---

### Exercice 3 : Diagnostic

#### 3.1 Le build qui échoue

**a. Cause précise de l'erreur** :  
Le fichier `requirements.txt` n'existe pas dans le contexte de build au moment où l'instruction `RUN pip install -r requirements.txt` est exécutée, car le `COPY . .` est placé **après** l'installation. Le répertoire `/app` est donc vide à ce stade.

**b. Correction du Dockerfile** :
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**c. Explication de l'erreur** :  
Cette erreur illustre une mauvaise compréhension de l'ordre des instructions dans un Dockerfile : le conteneur est construit couche par couche, et chaque instruction est exécutée dans l'ordre. L'étudiant a tenté d'installer les dépendances avant que le fichier `requirements.txt` ne soit copié, ce qui est impossible. Le build Docker reproduit fidèlement cet ordre, provoquant l'échec.

#### 3.2 Le conteneur qui ne voit pas l'autre

**a. L'erreur dans le DATABASE_URL** :  
Le code utilise `localhost`, qui dans le conteneur pointe vers le conteneur lui-même (127.0.0.1) et non vers l'hôte ou un autre conteneur. Le service `db` est donc inaccessible.

**b. Correction** :
```yaml
DATABASE_URL: "postgresql://user:password@db:5432/anfa"
```
**Explication** : Dans un réseau Docker Compose, les services sont accessibles via leur nom de service (`db` ici), et non via `localhost`. Docker Compose crée automatiquement un réseau où les noms des services résolvent les adresses IP des conteneurs correspondants.

---

### Exercice 4 : Optimisation d'image

#### 4.1 Identification des problèmes

| # | Problème | Explication |
|---|----------|-------------|
| 1 | **Base image trop lourde** | `ubuntu:22.04` est une image de 77 Mo ; `python:3.11-slim` serait plus légère (~50 Mo) et spécifique à Python. |
| 2 | **Multiples RUN non fusionnés** | Chaque `RUN` crée une couche intermédiaire ; une seule couche avec `&&` réduirait la taille et le nombre de couches. |
| 3 | **Cache APT non nettoyé** | Les paquets APT installés laissent des caches dans `/var/cache/apt` qui alourdissent l'image inutilement. |
| 4 | **Paquets inutiles** | `curl wget git build-essential` ne sont pas tous nécessaires ; `build-essential` est excessif pour une application qui ne compile pas. |
| 5 | **Absence de virtual environment** | `pip3 install` global peut causer des conflits de dépendances entre projets. |
| 6 | **Absence de `.dockerignore`** | Les fichiers inutiles (`.git`, `__pycache__`, etc.) alourdissent l'image. |

#### 4.2 Version optimisée du Dockerfile

```dockerfile
# 1. Image de base spécifique à Python, plus légère
FROM python:3.11-slim

# 2. Installation des dépendances système (une seule couche)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 3. Définition du répertoire de travail
WORKDIR /app

# 4. Copie des dépendances AVANT le code (optimisation cache)
COPY requirements.txt .

# 5. Installation des dépendances Python avec cache désactivé
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copie du code source (doit être ignoré par .dockerignore)
COPY . .

# 7. Création d'un utilisateur non-root
RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# 8. Point d'entrée
CMD ["python3", "downloader.py"]
```

---

### Exercice 5 : Mini-cas d'architecture

#### 5.1 Services à conteneuriser

| Service | Rôle |
|---------|------|
| **ftp-downloader** | Script Python qui se connecte au FTP, lit les fichiers JSON Lines, nettoie les données et les écrit dans MinIO. |
| **minio** | Serveur de stockage objet S3-compatible pour stocker les données agrégées. |
| **jupyter** | Environnement Jupyter Notebook pour l'exploration et la visualisation des données. |

#### 5.2 Politique de `restart` pour le script Python

Je recommande `restart: "no"` ou `restart: "on-failure"`.

**Justification** : Le script doit s'exécuter une fois par nuit (job ponctuel), pas rester en boucle. En cas d'échec, `on-failure` permet de réessayer automatiquement (utile pour des erreurs réseau temporaires), tandis que `always` provoquerait des exécutions répétitives inutiles et pourrait entraîner des traitements en double. Pour un job nocturne, `no` est aussi approprié si on utilise un scheduler externe (comme Cron ou Airflow).

#### 5.3 Mécanismes pour passer la date au script

| # | Mécanisme | Description | Recommandation |
|---|-----------|-------------|----------------|
| 1 | **Variable d'environnement** | `environment: PROCESS_DATE: "2026-06-23"` dans docker-compose. Le script lit `os.environ.get('PROCESS_DATE')`. | **Recommandé** : plus flexible, facilite l'intégration avec des orchestrateurs, utilisation de fichiers `.env`. |
| 2 | **Argument de la commande** | `command: ["python", "downloader.py", "2026-06-23"]` dans docker-compose. | Alternative valable mais moins flexible pour des modifications fréquentes. |

#### 5.4 Réponse à l'équipe

Un conteneur séparé pour le script ETL est préférable car il applique le principe de **séparation des responsabilités** : le script d'ingestion s'exécute en batch (une fois par nuit) et peut utiliser une politique de redémarrage différente (`on-failure`). Le notebook Jupyter, quant à lui, est interactif et doit rester accessible en continu pour l'exploration. Les séparer permet aussi de mettre à jour ou redémarrer l'un sans impacter l'autre, et de scaler individuellement chaque composant si nécessaire. De plus, cela évite de surcharger le conteneur Jupyter avec des dépendances ou des processus non liés à l'exploration.

#### 5.5 Squelette de `docker-compose.yml`

```yaml
version: "3.8"

services:
  # Service d'ingestion des données (script ETL)
  ftp-downloader:
    build:
      context: ./downloader
      dockerfile: Dockerfile
    image: anfa-downloader:latest
    container_name: anfa-downloader
    restart: "on-failure"  # Réessaie en cas d'échec
    environment:
      - FTP_HOST=${FTP_HOST:-ftp.example.com}
      - FTP_USER=${FTP_USER:-user}
      - FTP_PASSWORD=${FTP_PASSWORD:-password}
      - MINIO_ENDPOINT=${MINIO_ENDPOINT:-http://minio:9000}
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
      - BUCKET_NAME=${BUCKET_NAME:-anfa-data}
      - PROCESS_DATE=${PROCESS_DATE:-}  # Date à traiter (optionnelle)
    volumes:
      - ./data:/data  # Volume pour les fichiers temporaires
    depends_on:
      minio:
        condition: service_healthy
    networks:
      - anfa-network

  # Service MinIO (stockage objet)
  minio:
    image: minio/minio:latest
    container_name: anfa-minio
    restart: unless-stopped
    ports:
      - "9000:9000"   # API S3
      - "9001:9001"   # Console web
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin}
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    networks:
      - anfa-network

  # Service Jupyter Notebook
  jupyter:
    image: jupyter/pyspark-notebook:latest
    container_name: anfa-jupyter
    restart: unless-stopped
    ports:
      - "8888:8888"
    environment:
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-anfa-token}
      - MINIO_ENDPOINT=http://minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
      - BUCKET_NAME=${BUCKET_NAME:-anfa-data}
    volumes:
      - ./notebooks:/home/jovyan/work
      - ./data:/data
    depends_on:
      minio:
        condition: service_healthy
    networks:
      - anfa-network

# Définition des volumes persistants
volumes:
  minio-data:
    name: anfa-minio-data

# Définition du réseau commun
networks:
  anfa-network:
    name: anfa-network
    driver: bridge
```

#### 5.6 Fichier `.env` d'exemple

```env
# Variables communes
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
BUCKET_NAME=anfa-data
JUPYTER_TOKEN=anfa-token

# Variables FTP
FTP_HOST=ftp.example.com
FTP_USER=ftpuser
FTP_PASSWORD=ftppassword

# Date à traiter (YYYY-MM-DD)
PROCESS_DATE=2026-06-23
```

---

## Difficultés rencontrées

J'ai rencontré plusieurs difficultés lors de la réalisation de cette séance :

### 1. Connexion entre Jupyter et MinIO
- **Problème :** Les notebooks Jupyter n'arrivaient pas à se connecter au service MinIO.
- **Cause :** Le paramétrage des variables d'environnement et des endpoints MinIO n'était pas correct.
- **Solution :** J'ai corrigé les variables d'environnement en utilisant `minio:9000` comme endpoint dans le conteneur Jupyter, et j'ai configuré correctement les clés d'accès (`MINIO_ROOT_USER` et `MINIO_ROOT_PASSWORD`).

### 2. Cache Docker et reconstruction
- **Problème :** Docker ne réexécutait pas certaines étapes du Dockerfile lors de la reconstruction, ce qui provoquait l'utilisation d'anciennes versions du code.
- **Cause :** Le cache Docker utilise l'ordre des instructions et les modifications de contenu pour déterminer ce qui doit être reconstruit. Si une instruction `COPY . .` n'est pas modifiée, Docker utilise le cache.
- **Solution :** J'ai ajouté un `.dockerignore` pour exclure les fichiers inutiles et j'ai forcé la reconstruction avec `docker build --no-cache` lorsque c'était nécessaire. J'ai également organisé mon Dockerfile pour placer les instructions les moins susceptibles de changer en premier (comme `RUN apt-get install`), afin d'optimiser l'utilisation du cache.

### 3. Taille de l'image Docker
- **Problème :** L'image `anfa-analyse:v1` faisait 1.22 Go, ce qui est assez volumineux.
- **Cause :** L'image de base (`jupyter/pyspark-notebook`) intègre déjà de nombreuses dépendances, et l'ajout de nouvelles bibliothèques Python (`boto3`, `pandas`, etc.) alourdit l'image.
- **Solution :** J'ai testé le multi-stage build pour tenter de réduire la taille, mais comme expliqué dans la section bonus, l'impact a été minime. Une alternative serait d'utiliser une image de base plus légère, mais cela nécessiterait d'installer manuellement Spark et Jupyter, ce qui est plus complexe.

### 4. Gestion des permissions des volumes
- **Problème :** Les conteneurs ne parvenaient pas à écrire dans les volumes montés.
- **Cause :** Les permissions des répertoires sur l'hôte n'étaient pas compatibles avec l'utilisateur `jovyan` (UID 1000) utilisé dans le conteneur.
- **Solution :** J'ai ajusté les permissions des répertoires locaux avec `sudo chown -R 1000:1000 ./data` et j'ai configuré les volumes avec `:Z` sur certains systèmes pour gérer SELinux.

---

## Conclusion

Malgré ces difficultés, j'ai pu mener à bien l'ensemble des objectifs de la séance. La stack Docker Compose fonctionne correctement, le notebook Jupyter se connecte à MinIO et permet d'explorer les données du bucket `anfa-raw`. Cette séance m'a permis de maîtriser les concepts fondamentaux de la conteneurisation avec Docker et Docker Compose, ainsi que les bonnes pratiques pour optimiser les images. J'ai également acquis une meilleure compréhension des mécanismes de réseau inter-conteneurs, de gestion des volumes persistants et des stratégies d'optimisation des builds Docker.
```


