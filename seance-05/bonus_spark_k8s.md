# Bonus : Spark sur Kubernetes avec Spark Operator

##  Objectif du Bonus
Déployer un cluster Kubernetes local avec Kind, installer le Spark Operator, et soumettre un job Spark via un manifeste YAML déclaratif. Cette approche permet de gérer les applications Spark comme des ressources natives Kubernetes.

---

##  Prérequis
- Docker Desktop
- Kind (Kubernetes in Docker)
- kubectl
- Helm (installé manuellement)
- Accès Internet

---

##  Étape 1 : Création du Cluster Kind


kind create cluster --name anfa
Résultat :

text
Creating cluster "anfa" ...
✓ Ensuring node image (kindest/node:v1.36.1) 
✓ Preparing nodes 
✓ Writing configuration 
✓ Starting control-plane 
✓ Installing CNI 
✓ Installing StorageClass 
Set kubectl context to "kind-anfa"
Vérification :

bash
kubectl get nodes
kubectl cluster-info --context kind-anfa
Création du namespace :

bash
kubectl create namespace spark
 Étape 2 : Installation de Helm
Problème : Helm non installé
Erreur : helm : Le terme «helm» n'est pas reconnu...

Solution - Installation manuelle :

powershell
# Télécharger Helm
Invoke-WebRequest -Uri "https://get.helm.sh/helm-v3.17.0-windows-amd64.zip" -OutFile "helm.zip"
Expand-Archive -Path "helm.zip" -DestinationPath "."
Copy-Item ".\windows-amd64\helm.exe" -Destination "$env:USERPROFILE\helm\helm.exe"
$env:Path += ";$env:USERPROFILE\helm"

# Vérifier
helm version
Résultat :

text
version.BuildInfo{Version:"v3.17.0", GitCommit:"..."}
 Étape 3 : Installation du Spark Operator
3.1 Tentative avec Helm (Échec)
bash
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update
helm install spark-operator spark-operator/spark-operator \
  --namespace spark-operator \
  --create-namespace \
  --wait \
  --timeout 10m
Erreur :

text
Error: INSTALLATION FAILED: context deadline exceeded
Cause : Timeout lors du téléchargement des images.

3.2 Installation Manuelle (Solution)
bash
# Nettoyer
helm uninstall spark-operator -n spark-operator 2>/dev/null

# Télécharger le manifeste
wget https://raw.githubusercontent.com/kubeflow/spark-operator/v1.2.4/manifests/spark-operator.yaml

# Appliquer
kubectl create namespace spark-operator
kubectl apply -f spark-operator.yaml
Vérification :

bash
kubectl get pods -n spark-operator
Résultat :

text
NAME                              READY   STATUS    RESTARTS   AGE
spark-operator-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
 Étape 4 : Construction de l'Image Docker Personnalisée
4.1 Dockerfile (Dockerfile.spark-k8s)
dockerfile
FROM bitnami/spark:3.5.8

USER root

# Installer boto3
RUN pip3 install --upgrade pip && \
    pip3 install boto3

# Copier les scripts
RUN mkdir -p /opt/jobs
COPY jobs/*.py /opt/jobs/
RUN chmod -R 755 /opt/jobs

USER 1001
WORKDIR /opt/jobs
4.2 Construction de l'Image
bash
docker build -f Dockerfile.spark-k8s -t spark-job:latest .
4.3 Problème : Build avec apache/spark:latest
Erreur :

text
E: Failed to fetch http://archive.ubuntu.com/ubuntu/dists/jammy/universe/binary-amd64/Packages
Connection failed [IP: 172.66.152.176 80]
Solution : Utilisation de l'image bitnami/spark:3.5.8 (plus légère et stable).

4.4 Chargement dans Kind
bash
kind load docker-image spark-job:latest --name anfa
Résultat :

text
Image: "spark-job:latest" with ID "sha256:..." loaded into Kind cluster "anfa"
 Étape 5 : Création du Secret MinIO
bash
kubectl create secret generic minio-credentials \
  --namespace spark \
  --from-literal=access-key=minioadmin \
  --from-literal=secret-key=minioadmin
 Étape 6 : Manifeste SparkApplication
Fichier : spark-job.yaml

yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: anfa-heures-pointe
  namespace: spark
spec:
  type: Python
  mode: cluster
  image: spark-job:latest
  imagePullPolicy: IfNotPresent
  mainApplicationFile: local:///opt/jobs/heures_de_pointe.py
  sparkVersion: 3.5.8
  restartPolicy:
    type: Never
  
  sparkConf:
    "spark.jars.ivy": "/tmp/.ivy2"
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000"
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem"
    "spark.hadoop.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    "spark.hadoop.fs.s3a.access.key": "minioadmin"
    "spark.hadoop.fs.s3a.secret.key": "minioadmin"
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false"
    "spark.hadoop.fs.s3a.path.style.access": "true"
  
  deps:
    packages:
      - "org.apache.hadoop:hadoop-aws:3.3.4"
      - "com.amazonaws:aws-java-sdk-bundle:1.12.262"
  
  driver:
    cores: 1
    memory: 1024m
    env:
      - name: HOME
        value: /tmp
      - name: PYTHONPATH
        value: /usr/local/lib/python3.10/dist-packages
  
  executor:
    cores: 1
    memory: 1024m
    instances: 2
    env:
      - name: HOME
        value: /tmp
      - name: PYTHONPATH
        value: /usr/local/lib/python3.10/dist-packages
 Étape 7 : Soumission du Job
bash
# Appliquer le manifeste
kubectl apply -f spark-job.yaml
Résultat :

text
sparkapplication.sparkoperator.k8s.io/anfa-heures-pointe created
7.1 Suivi de l'Exécution
bash
# Voir l'état
kubectl get sparkapp -n spark

# Voir les pods
kubectl get pods -n spark

# Logs du driver
kubectl logs -f anfa-heures-pointe-driver -n spark
7.2 Résultat de l'Analyse
text
============================================================
  ANFA  ANALYSE DES HEURES DE POINTE
============================================================

  Trajets analysés : 79,368

  Top 10 des heures les plus chargées par ligne :
+--------+-----+----------+---------------+-----------------+
|ligne_id|heure|nb_trajets|total_passagers|retard_moyen     |
+--------+-----+----------+---------------+-----------------+
|L08     |18   |841       |34485          |8.500594530321047|
|L08     |8    |836       |34255          |8.46531100478469 |
|L09     |18   |827       |34118          |8.45223700120919 |
|L10     |18   |840       |34017          |8.478571428571428|
|L06     |8    |836       |34009          |8.421052631578947|
|L02     |18   |819       |33858          |8.454212454212454|
|L09     |8    |819       |33847          |8.487179487179487|
|L11     |18   |820       |33758          |8.519512195121951|
|L07     |18   |820       |33633          |8.55609756097561 |
|L01     |8    |816       |33469          |8.534313725490197|
+--------+-----+----------+---------------+-----------------+

  [OK] Résultats écrits dans s3a://anfa-processed/heures_de_pointe/
============================================================
 Problèmes Rencontrés et Solutions
Problème	Cause	Solution
helm: command not found	Helm non installé	Installation manuelle du binaire
context deadline exceeded	Timeout Helm	Installation manuelle via kubectl
apt-get: connection failed	Problème réseau Ubuntu	Utilisation de l'image bitnami/spark
image not present locally	Image non chargée dans Kind	kind load docker-image spark-job:latest --name anfa
boto3 module not found	boto3 non installé	pip3 install boto3 dans Dockerfile
Connection refused to MinIO	Mauvaise configuration S3	Ajout des paramètres S3 dans sparkConf
 Comparaison Docker Compose vs Kubernetes
Aspect	Docker Compose	Kubernetes + Spark Operator
Déploiement	Manuelle (docker compose up)	Déclaratif (YAML)
Scalabilité	Fixe (workers définis)	Élastique (ajout/retrait de pods)
Gestion des échecs	Manuelle	Automatique (l'opérateur gère)
Monitoring	Limité (logs)	Avancé (kubectl, métriques)
Résilience	Faible	Élevée (redémarrage automatique)
Production	Non recommandé	Recommandé
 Commandes Utiles pour Kubernetes
bash
# Gestion du cluster
kind get clusters
kind delete cluster --name anfa

# Spark Operator
kubectl get pods -n spark-operator
kubectl logs -n spark-operator deployment/spark-operator

# SparkApplication
kubectl get sparkapp -n spark
kubectl describe sparkapp anfa-heures-pointe -n spark
kubectl delete sparkapp anfa-heures-pointe -n spark

# Logs
kubectl logs -f anfa-heures-pointe-driver -n spark
kubectl logs anfa-heures-pointe-exec-1 -n spark

# Nettoyage complet
kubectl delete namespace spark
kubectl delete namespace spark-operator
kind delete cluster --name anfa
 Conclusion du Bonus
Objectifs atteints :

 Cluster Kind créé et fonctionnel

 Spark Operator installé (via méthode manuelle)

 Image Docker personnalisée construite et chargée

 Manifeste SparkApplication créé

 Job Spark soumis avec succès

 Résultats identiques à l'exécution Docker Compose

Valeur ajoutée :

Gestion déclarative des jobs Spark

Meilleure résilience et scalabilité

Approche "Cloud Native"

Facilité d'intégration dans une chaîne CI/CD

 Structure des Fichiers Bonus
text
seance-05/
├── jobs/
│   ├── heures_de_pointe.py
│   ├── generer_trajets.py
│   └── analyse_referentiel_cluster.py
├── résultats/
│   └── bonus_spark_k8s.md        # Ce fichier
├── Dockerfile.spark-k8s
├── spark-job.yaml
├── spark-operator.yaml
├── docker-compose.yml
└── RENDU.md
 Références
Spark Operator GitHub

Kind Documentation

Helm Documentation

Bitnami Spark Image

Date : 30 Juin 2026
Auteur : KOMBATE GARIBA Moubarak

text

---
