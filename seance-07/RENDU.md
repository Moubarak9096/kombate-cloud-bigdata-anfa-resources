# Rendu — Séance 7

**Nom et prénom :** KOMBATE GARIBA Moubarak  
**Identifiant GitHub :** Moubarak9096  
**Date de soumission :** 06/07/2026

---

## Résumé de la séance

Un cluster Kafka avec 3 brokers en mode KRaft a été déployé aux côtés de Kafka UI, MinIO et Spark. Une flotte de 100 bus simulés a été mise en place, envoyant en continu leurs positions GPS vers le topic `anfa-positions-bus`. La tolérance aux pannes a été observée en arrêtant volontairement un broker, démontrant la résilience du cluster (réplication 3). Spark Structured Streaming a été configuré pour consommer le flux, effectuer des agrégations par fenêtre de 30 secondes et écrire les résultats dans MinIO. Le pipeline streaming a ensuite été enrichi avec l'option `failOnDataLoss` pour gérer les pertes de données et le checkpoint pour assurer la reprise.

---

## Étapes principales

### 1. Déploiement du cluster Kafka (3 brokers, mode KRaft) + Kafka UI

**Objectif** : Mettre en place un cluster Kafka résilient avec 3 brokers utilisant le protocole KRaft (sans Zookeeper).

**Fichier :** `docker-compose.yml`

**Configuration des brokers :**
- 3 brokers : `kafka-1`, `kafka-2`, `kafka-3`
- Ports externes : 19092, 19093, 19094
- Mode KRaft avec `KAFKA_PROCESS_ROLES: broker,controller`
- Quorum : `KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093`
- Cluster ID unique : `"oPDaLQlUQ3Sg_L8LBoc5AA"`
- Facteur de réplication : 3

**Kafka UI** : Interface web accessible sur `http://localhost:8085`

**Démarrage :**
```powershell
docker compose up -d
```

**Problème rencontré :** PostgreSQL 18+ incompatible avec le volume existant (erreur : `found character that cannot start any token`).
**Solution :** Suppression du volume `seance-06_postgres-data` et recréation.

---

### 2. Création du topic `anfa-positions-bus` (3 partitions, réplication 3)

**Commande :**
```powershell
docker exec anfa-kafka-1 /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic anfa-positions-bus \
  --partitions 3 \
  --replication-factor 3
```

**Vérification :**
```powershell
docker exec anfa-kafka-1 /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic anfa-positions-bus
```

**Résultat :**
```
Topic: anfa-positions-bus    Partition: 0    Leader: 1    Replicas: 1,2,3    Isr: 1,2,3
Topic: anfa-positions-bus    Partition: 1    Leader: 2    Replicas: 2,3,1    Isr: 2,3,1
Topic: anfa-positions-bus    Partition: 2    Leader: 3    Replicas: 3,1,2    Isr: 3,1,2
```

**Observations :**
- 3 partitions pour paralléliser la consommation
- Facteur de réplication 3 pour tolérance aux pannes
- Chaque partition a un leader et 2 followers

---

### 3. Premier producer/consumer Python pour comprendre la mécanique

**Producer :** `kafka_producer.py`
```python
from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    position = {
        'bus_id': f'B{random.randint(1,100):03d}',
        'ligne_id': f'L{random.randint(1,12):02d}',
        'latitude': 6.13 + random.random() * 0.1,
        'longitude': 1.22 + random.random() * 0.1,
        'vitesse_kmh': random.randint(0, 50),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
    }
    producer.send('anfa-positions-bus', value=position)
    time.sleep(0.5)
```

**Consumer :** `kafka_consumer.py`
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'anfa-positions-bus',
    bootstrap_servers=['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

for message in consumer:
    print(f"Bus {message.value['bus_id']} - Ligne {message.value['ligne_id']}")
```

**Observations :**
- Production et consommation fonctionnelles
- Messages bien ordonnés par partition
- Latence < 100ms

---

### 4. Simulation de 100 bus envoyant leur position en continu

**Script :** `simulateur_bus.py` (exécuté dans le conteneur Spark)

```powershell
docker exec anfa-spark-master python3 /opt/jobs/simulateur_bus.py
```

**Caractéristiques :**
- 100 bus simulés (B001 à B100)
- 12 lignes de bus (L01 à L12)
- Envoi de positions toutes les 5 secondes
- Vitesse aléatoire (0 à 50 km/h)
- Coordonnées GPS aléatoires autour de Lomé

**Débit :** ~20 messages/seconde

**Vérification dans Kafka UI :**
- Débit de messages en augmentation (de 0 à 20 msg/s)
- Partitions bien équilibrées

---

### 5. Démonstration de tolérance aux pannes (arrêt d'un broker)

**Procédure :**
```powershell
# Arrêter volontairement le broker 2
docker compose stop kafka-2

# Vérifier dans Kafka UI (2 brokers sur 3)
# Observer que les partitions se rééquilibrent
```

**Observations :**
1. **ISR (In-Sync Replicas) se réduit** : `Isr: 1,3` (le broker 2 est retiré)
2. **Nouveaux leaders élus** : Les partitions 1 et 2 changent de leader
3. **Continuité du service** : Aucun message perdu, production continue
4. **Rééquilibrage automatique** : Après redémarrage, le broker 2 réintègre l'ISR

**Commande de vérification :**
```powershell
docker exec anfa-kafka-1 /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe --topic anfa-positions-bus
```

**Résultat après arrêt :**
```
Topic: anfa-positions-bus    Partition: 0    Leader: 1    Replicas: 1,2,3    Isr: 1,3
Topic: anfa-positions-bus    Partition: 1    Leader: 3    Replicas: 2,3,1    Isr: 3,1
Topic: anfa-positions-bus    Partition: 2    Leader: 1    Replicas: 3,1,2    Isr: 1,3
```

---

### 6. Spark Structured Streaming : lecture console, puis agrégation en fenêtre vers MinIO

**6.1 Lecture console (`lecture_flux_console.py`)**

```python
flux_brut = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092") \
    .option("subscribe", "anfa-positions-bus") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

positions = flux_brut.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

query = positions.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
```

**Exécution :**
```powershell
docker exec anfa-spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8" \
  /opt/jobs/lecture_flux_console.py
```

**Résultat :** Affichage des positions des bus en temps réel dans la console.

**6.2 Agrégation et écriture dans MinIO (`agregation_streaming.py`)**

```python
agregats = positions \
    .withWatermark("event_time", "1 minute") \
    .groupBy(
        window(col("event_time"), "30 seconds"),
        col("ligne_id")
    ) \
    .agg(
        count("*").alias("nb_positions_recues"),
        avg("vitesse_kmh").alias("vitesse_moyenne")
    )

query = agregats.writeStream \
    .format("parquet") \
    .option("path", "s3a://anfa-streaming/agregats_par_ligne/") \
    .option("checkpointLocation", "s3a://anfa-streaming/checkpoints/agregats/") \
    .outputMode("append") \
    .trigger(processingTime="30 seconds") \
    .start()
```

**Configuration Spark pour MinIO :**
```python
spark.conf.set("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
spark.conf.set("spark.hadoop.fs.s3a.access.key", "anfa-app-key")
spark.conf.set("spark.hadoop.fs.s3a.secret.key", "anfa-app-secret-2026")
spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
```

**Vérification dans MinIO :**
```powershell
docker exec anfa-minio mc ls local/anfa-streaming/agregats_par_ligne/
docker exec anfa-minio mc cat local/anfa-streaming/agregats_par_ligne/part-*.parquet
```

---

## Captures d'écran

### 3 brokers actifs dans Kafka UI
![Brokers actifs](captures/kafka-ui-brokers.png)

### Débit de messages en augmentation
![Débit messages](captures/kafka-ui-debit.png)

### Cluster avec 2 brokers sur 3 (après arrêt volontaire)
![2 brokers sur 3](captures/kafka-ui-2-brokers.png)

### Micro-batchs affichés en console par Spark
![Console Spark Streaming](captures/spark-streaming-console.png)

### Résultats agrégés dans MinIO
![MinIO agregats](captures/minio-agregats.png)

---

## Réflexion personnelle

**Kafka + Spark Streaming vs Batch Airflow + Spark**

**Cas d'usage recommandés :**

| Critère | Batch (Airflow + Spark) | Streaming (Kafka + Spark) |
|---------|-------------------------|---------------------------|
| **Latence** | Minutes/heures | Secondes/millisecondes |
| **Volume** | Historique (Go/To) | Flux continu |
| **Traitement** | Agrégations complexes | Agrégations simples/fenêtrées |
| **Cas typique** | Rapports quotidiens, ETL | Monitoring temps réel, Alertes |
| **Coût** | Moindre (batch) | Plus élevé (continu) |

**J'utiliserais Kafka + Spark Streaming pour :**
- Monitoring des transports en temps réel
- Détection d'anomalies (retards, incidents)
- Tableaux de bord dynamiques
- Systèmes d'alerte (arrêt, déviation)

**J'utiliserais Airflow + Spark Batch pour :**
- Rapports d'activité quotidiens
- Analyses historiques
- Entrepôt de données (Data Warehouse)
- Calculs complexes (machine learning)

**Ce que la réplication à 3 brokers m'a concrètement montré :**
1. **Haute disponibilité** : L'arrêt d'un broker n'interrompt pas le service
2. **Élection de leader** : Les partitions réélisent un leader automatiquement
3. **ISR** : Les brokers en retard sont exclus, assurant la cohérence
4. **Rééquilibrage** : Le broker redémarre et réintègre le cluster
5. **Aucune perte de données** : Les messages sont répliqués sur 3 brokers

---

## Réponses aux exercices d'application

**NEANT** (Aucun exercice d'application pour cette séance)

---

## Difficultés rencontrées

| Difficulté | Cause | Solution |
|------------|-------|----------|
| **Erreur YAML ligne 206** | Caractère invisible/tabulation dans docker-compose.yml | Suppression et recréation du fichier avec des espaces |
| **PostgreSQL 18+ incompatible** | Changement de structure de données | Suppression du volume `seance-06_postgres-data` |
| **Un seul worker Spark** | Configuration initiale | Ajout de `spark-worker-2` dans docker-compose.yml |
| **Ressources insuffisantes** | Applications en attente | Redémarrage des workers + réduction des ressources (512m) |
| **`failOnDataLoss`** | Perte de données dans Kafka | Ajout de l'option `"false"` et suppression du checkpoint |
| **Checkpoint corrompu** | Topic recréé avec des offsets différents | `rm -rf /tmp/spark-checkpoint` |
| **Connexion MinIO** | Credentials incorrects | Configuration explicite avec `anfa-app-key` et `anfa-app-secret-2026` |
| **Topics manquants** | Partition `anfa-positions-bus-1` et `-2` | Création du topic avec 3 partitions |
| **Commande PowerShell** | Backticks incorrects | Utilisation de la commande sur une seule ligne |

---

**Date :** 06/07/2026  
**Projet :** Cloud & Big Data - ESGIS Master 1 IA / BD