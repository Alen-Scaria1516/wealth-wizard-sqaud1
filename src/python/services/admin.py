from utils.utilities_for_admin import export_verification_logs_to_txt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, min as spark_min, max as spark_max, avg, count, when, unix_timestamp
from pyspark.sql.functions import concat_ws
#export as a txt file
def setup_pyspark():
    export_verification_logs_to_txt()
    spark = SparkSession.builder.appName("Project").getOrCreate()
    df = spark.read.json(r"src\python\data_files\verification_logs.txt")
    return df
#df.show()
#df.printSchema()
def compute_verification_stats(df):
    # Flatten
    flat_df = df.select(
        col("email_id"),
        col("category"),
        col("action"),
        col("details.attempt_number").alias("attempt_number"),
        col("details.status").alias("status"),
        col("timestamp.$date").alias("timestamp")
    )
    
    flat_df = flat_df.filter(col("category") == 'VERIFICATION')
    # Convert timestamp string to proper timestamp
    flat_df = flat_df.withColumn("timestamp", col("timestamp").cast("timestamp"))

    flat_df.toPandas().to_csv(r"src\python\data_files\flat_df.csv", index=False)


    # Token generation time
    token_time = flat_df.filter(col("action") == "TOKEN_GENERATED") \
                        .groupBy("email_id") \
                        .agg(spark_min("timestamp").alias("token_time"))
    
    # Successful verification time
    success_time = flat_df.filter((col("action") == "ATTEMPT") & (col("status") == True)) \
                          .groupBy("email_id") \
                          .agg(spark_min("timestamp").alias("success_time"),
                               spark_min("attempt_number").alias("attempts"))
    
    # Join to compute time taken
    result = token_time.join(success_time, on="email_id", how="inner") \
                       .withColumn("time_taken_secs",
                                   unix_timestamp("success_time") - unix_timestamp("token_time"))
    
    # Now aggregate global stats
    stats = result.agg(
        count("*").alias("Total Verifications"),
        (count(when(col("success_time").isNotNull(), 1)) / count("*") * 100).alias("Success %"),
        avg("attempts").alias("Avg Attempts"),
        spark_max("attempts").alias("Max Attempts"),
        avg("time_taken_secs").alias("Avg Time Taken (secs)")
    )
    
    return stats

def admin_verification_stats():
    df = setup_pyspark()
    verification_stats_df = compute_verification_stats(df)
    verification_stats_df.show(truncate=False)