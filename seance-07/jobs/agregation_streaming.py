"""
agregation_streaming.py
─────────────────────────
Consomme le flux de positions GPS, calcule des agrégats par fenêtre
de 30 secondes et par ligne, et écrit les résultats dans MinIO.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType
from pyspark.sql.functions import col, from_json, window, count, avg, to_timestamp


def creer_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Anfa - Agrégation streaming")
        .master("spark://spark-master:7077")
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
        .config("spark.hadoop.fs.s3a.access.key", "anfa-app-key")
        .config("spark.hadoop.fs.s3a.secret.key", "anfa-app-secret-2026")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8,"
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        )
        .getOrCreate()
    )


def main():
    spark = creer_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    schema_position = (
        StructType()
        .add("bus_id", StringType())
        .add("ligne_id", StringType())
        .add("latitude", DoubleType())
        .add("longitude", DoubleType())
        .add("vitesse_kmh", IntegerType())
        .add("timestamp", StringType())
    )

    flux_brut = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092")
        .option("subscribe", "anfa-positions-bus")
        .option("startingOffsets", "latest")
        .load()
    )

    positions = (
        flux_brut
        .select(from_json(col("value").cast("string"), schema_position).alias("data"))
        .select("data.*")
        .withColumn("event_time", to_timestamp(col("timestamp")))
    )

    # ── Agrégation par fenêtre de 30 secondes et par ligne ──
    agregats = (
        positions
        .withWatermark("event_time", "1 minute")   # tolère 1 min de retard des messages
        .groupBy(
            window(col("event_time"), "30 seconds"),
            col("ligne_id"),
        )
        .agg(
            count("*").alias("nb_positions_recues"),
            avg("vitesse_kmh").alias("vitesse_moyenne"),
        )
    )

    # ── Écriture en streaming vers MinIO, au format Parquet ──
    requete = (
        agregats.writeStream
        .format("parquet")
        .option("path", "s3a://anfa-streaming/agregats_par_ligne/")
        .option("checkpointLocation", "s3a://anfa-streaming/checkpoints/agregats/")
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .start()
    )

    requete.awaitTermination()


if __name__ == "__main__":
    main()
