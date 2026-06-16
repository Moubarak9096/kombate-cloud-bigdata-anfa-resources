# Cloud & Big Data — Ressources du cours

ESGIS
Master 1 Intelligence Artificielle et Big Data
Année universitaire 2025-2026

Enseignant : **Denis AKPAGNONITE**

---

## Le projet : Anfa

Ce dépôt accompagne l'UE « Cloud & Big Data ». Il sert de support à un projet fil rouge appelé **Anfa** : une plateforme data construite tout au long du module pour le compte d'une société (fictive) de transport public urbain à Lomé. Cette société exploite une centaine de bus sur les principales lignes de la ville et souhaite passer d'une exploitation à l'aveugle à un pilotage par la donnée : heures de pointe, zones de forte affluence, prédiction des temps de trajet, segmentation des passagers, modes de paiement, types d'abonnement, etc.

Chaque séance ajoute une brique à cette plateforme. En fin de module, vous disposerez d'une stack data complète, fonctionnelle et déployable.

---

## Structure du dépôt

```
cloud-bigdata-anfa-resources/
├── README.md                  ← vous êtes ici
├── .gitignore                 ← fichiers ignorés par Git
├── .dockerignore              ← modèle de référence pour vos builds Docker
├── data/                      ← le patrimoine de données d'Anfa (partagé entre séances)
│   └── referentiel/
│       ├── lignes.csv
│       ├── arrets.csv
│       ├── bus.csv
│       └── tarifs.csv
```

Le dossier `data/` est la **source de vérité** pour les datasets du projet. Vous le consommez en lecture seule depuis vos scripts. Il s'enrichira au fil du module : `data/trajets/`, `data/validations/`, `data/meteo/`, etc.

---

## Workflow étudiant

### 1. Une fois en début de module

**Forker ce dépôt sur votre compte GitHub.**

1. Cliquez sur le bouton **Fork** en haut à droite de la page du dépôt.
2. Choisissez le nom de votre fork (vous le communiquerez sur **Google Classroom**).
3. Clonez votre fork localement :

```bash
git clone https://github.com/<votre-username>/cloud-bigdata-anfa-resources.git
cd cloud-bigdata-anfa-resources
```

### 2. À chaque séance N

**Créer une branche dédiée à la séance**, en respectant strictement la convention de nommage :

```bash
# Convention : seance-NN avec un zéro de remplissage (seance-01 à seance-12)
git checkout main
git pull                              # récupérer les éventuelles mises à jour du tronc
git checkout -b seance-NN
```

Travaillez ensuite dans le dossier `seance-NN/` (que vous créez), poussez votre branche sur votre fork, puis soumettez l'URL de la branche dans **Google Classroom**.

### 3. Récupérer les nouveaux datasets publiés

Quand de nouvelles données sont ajoutées pour une séance à venir, synchronisez votre fork avec le dépôt d'origine :

**Méthode simple (via l'interface GitHub)** : sur la page de votre fork, cliquez sur **Sync fork** → **Update branch**.

**Méthode CLI** :

```bash
# Une seule fois : déclarer le dépôt d'origine comme "upstream"
git remote add upstream https://github.com/<compte-cours>/cloud-bigdata-anfa-resources.git

# À chaque mise à jour annoncée
git fetch upstream
git checkout main
git merge upstream/main
git push
```

---

## Convention de nommage des branches

| Branche      | Séance |
|--------------|--------|
| `main`       | Tronc commun (n'est jamais modifié directement par les étudiants) |
| `seance-01`  | Séance 1 — Fondamentaux du Cloud + Docker + MinIO |
| `seance-02`  | Séance 2 — Docker en profondeur |
| `seance-03`  | Séance 3 — Kubernetes |
| `seance-04`  | Séance 4 — Infrastructure as Code (Terraform) |
| `seance-05`  | Séance 5 — Cluster Spark |
| `seance-06`  | Séance 6 — Pipelines de données (Airflow) |
| `seance-07`  | Séance 7 — Streaming (Kafka) |
| `seance-08`  | Séance 8 — CI/CD (GitHub Actions) |
| `seance-09`  | Séance 9 — Monitoring (Prometheus + Grafana) |
| `seance-10`  | Séance 10 — MLOps (MLflow) |
| `seance-11`  | Séance 11 — Sécurité, gouvernance, coûts |
| `seance-12`  | Séance 12 — Projet intégrateur |

Le respect strict de cette convention est nécessaire pour la correction.

---

## Évaluation et soumissions

| Composante                        | Poids |
|-----------------------------------|-------|
| Travaux pratiques (sur GitHub)    | 30 %  |
| Projet intégrateur (séance 12)    | 40 %  |
| Examen écrit                      | 30 %  |

Toutes les soumissions de TP se font via **Google Classroom**, où vous déposez l'URL de votre branche après chaque séance. Le lien Classroom du cours vous sera communiqué en début de semestre.

---

## Stack technique du cours

Tout est open source et déployable localement, sans compte cloud payant.

| Besoin                  | Outil                          |
|-------------------------|--------------------------------|
| Conteneurisation        | Docker, Docker Compose         |
| Orchestration           | Kubernetes (Minikube)          |
| Infrastructure as Code  | Terraform                      |
| CI/CD                   | GitHub Actions                 |
| Stockage objet          | MinIO (compatible S3)          |
| Orchestration data      | Apache Airflow                 |
| Streaming               | Apache Kafka                   |
| Traitement distribué    | Apache Spark (PySpark)         |
| MLOps                   | MLflow                         |
| Monitoring              | Prometheus + Grafana           |

---

## Contact

Pour toute question : Laisser un commentaire sur **Google Classroom** ou envoyer un email à **Denis AKPAGNONITE**