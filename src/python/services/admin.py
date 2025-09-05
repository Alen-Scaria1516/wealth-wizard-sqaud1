from utils.utilities_for_admin import export_logs_to_txt
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, desc, date_format, when,
    dayofweek, avg, min as spark_min, max as spark_max,
    count, unix_timestamp, weekofyear, month
)
from datetime import datetime, timedelta


#start the pyspark session
def setup_pyspark():
    export_logs_to_txt()
    spark = SparkSession.builder.appName("Project").getOrCreate()
    df = spark.read.json(r"src\python\data_files\logs.txt")
    return df
#df.show()
#df.printSchema()

#Registration Stats
def compute_registration_analysis(df):
    try:
        df = df.withColumn("timestamp", to_timestamp(col("timestamp.$date")))

        # 1. Total Attempts and Success
        total_attempts = df.filter(col("action") == "ATTEMPT").count()
        total_registered = df.filter(col("action") == "REGISTERED").count()
        print(f"   Total Registration Attempts: {total_attempts}")
        print(f"   Successful Registrations: {total_registered}")
        print(f"   Registration Success Rate: {(total_registered / total_attempts * 100):.2f}%")

        # 2. Registration Flow Analysis
        print("\n2. Registration Flow Analysis:")
        flow_analysis = df.groupBy("action").count().orderBy(desc("count"))
        flow_analysis.show()

        # 3. Daily Registration Trends (Last 30 days)
        print("\n3. Daily Registration Trends (Last 30 days):")
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_logs = df.filter(col("timestamp") >= thirty_days_ago)

        daily_trends = recent_logs.groupBy(
            date_format(col("timestamp"), "yyyy-MM-dd").alias("date"),
            col("action")
        ).count().orderBy("date", "action")

        daily_trends.show()

        # 4. Registration Success vs Failure Analysis
        print("\n4. Registration Success vs Failure Analysis:")
        success_failure = df.filter(col("action") == "ATTEMPT") \
            .select("email_id", "details.status") \
            .groupBy("status").count()

        success_failure.show()

        # 5. Age Group Analysis (from registered users)
        print("\n5. Age Group Analysis:")
        registered_users = df.filter(col("action") == "REGISTERED") \
            .select("details.age") \
            .filter(col("age").isNotNull())

        if registered_users.count() > 0:
            age_groups = registered_users.select(
                when(col("age") < 25, "18-24")
                .when(col("age").between(25, 34), "25-34")
                .when(col("age").between(35, 44), "35-44")
                .when(col("age").between(45, 54), "45-54")
                .when(col("age").between(55, 64), "55-64")
                .otherwise("65+")
                .alias("age_group")
            ).groupBy("age_group").count().orderBy("age_group")

            age_groups.show()

            # Average age
            avg_age = registered_users.agg(avg("age")).collect()[0][0]
            print(f"   Average Age: {avg_age:.2f} years")

        # 6. Weekly Registration Patterns
        print("\n6. Weekly Registration Patterns:")
        weekly_patterns = df.groupBy(
            dayofweek(col("timestamp")).alias("day_of_week"),
            col("action")
        ).count().orderBy("day_of_week", "action")

        weekly_patterns.show()

        return True

    except Exception as e:
        print(f"Analysis failed: {e}")
        return None

#Login stats 
def compute_login_stats(file_path):
    spark = SparkSession.builder \
        .appName("LoginAnalytics") \
        .master("local[*]") \
        .getOrCreate()

    # print(" Spark started:", spark.version)
    df = spark.read.option("multiline", "true").json(file_path)
    df = df.withColumn("ts", to_timestamp(col("timestamp.$date")))
    df = df.withColumn("status", col("details.status"))

    # ----------------- Success vs Failure -----------------
    print("\n Success vs Failure Login Count")
    success_fail = df.groupBy("status").count()
    success_fail.show()

    # ----------------- Logins per Day -----------------
    print("\n Logins per Day")
    logins_per_day = df.groupBy(date_format("ts", "yyyy-MM-dd").alias("date")) \
                       .count() \
                       .orderBy("date")
    logins_per_day.show(10, truncate=False)

    # ----------------- Logins per Week -----------------
    print("\n Logins per Week")
    logins_per_week = df.groupBy(weekofyear("ts").alias("week")) \
                        .count() \
                        .orderBy("week")
    logins_per_week.show(10, truncate=False)

    # ----------------- Logins per Month -----------------
    print("\n Logins per Month")
    logins_per_month = df.groupBy(month("ts").alias("month")) \
                         .count() \
                         .orderBy("month")
    logins_per_month.show()

    # ----------------- High login days -----------------
    print("\n High Login Days (count > 2)")
    high_login_days = logins_per_day.filter(col("count") > 2).orderBy("date")
    high_login_days.show()

    # ----------------- Failed reasons -----------------
    print("\n Failed Login Attempts by Reason")
    logs_df = df.select(
        col("email_id"),
        col("action"),
        col("details.attempt_number").alias("attempt_number"),
        col("details.status").alias("status"),
        col("details.reason").alias("reason"),
        col("timestamp.$date").alias("timestamp")
    ).filter(col("reason").isNotNull())

    reason_counts = logs_df.groupBy("reason") \
                           .count() \
                           .orderBy(col("count").desc())
    reason_counts.show(truncate=False)
    spark.stop()
    return {
        "success_fail": success_fail,
        "logins_per_day": logins_per_day,
        "logins_per_week": logins_per_week,
        "logins_per_month": logins_per_month,
        "high_login_days": high_login_days,
        "reason_counts": reason_counts
    }
    
#PasswordReset Stats
def compute_passwordReset_stats(df):
    # Flatten relevant fields
    flat_df = df.select(
        col("email_id"),
        col("category"),
        col("action"),
        col("timestamp.$date").alias("timestamp")
    )

    # Filter only PASSWORD_RESET logs
    flat_df = flat_df.filter(col("category") == "PASSWORD_RESET")

    # Convert timestamp string to proper timestamp
    flat_df = flat_df.withColumn("timestamp", col("timestamp").cast("timestamp"))

    # Count resets per user (count all actions related to password reset for a user)
    user_reset_counts = flat_df.groupBy("email_id").agg(count("*").alias("reset_count"))

    # Global aggregations
    stats = user_reset_counts.agg(
        count("*").alias("Total Users Who Reset Password"),
        avg("reset_count").alias("Avg Resets per User"),
        spark_max("reset_count").alias("Max Resets by a User")
    )

    # Also compute total resets across all users
    total_resets = flat_df.count()

    # Add total resets as a separate column
    stats = stats.withColumn("Total Password Resets", col("Total Users Who Reset Password") * 0 + total_resets)
    stats.show(truncate=False)
    return stats
     
# Verification Stats
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
     while True:
        print("\n=== Admin Menu ===")
        print("1. Registration Stats")
        print("2. Login stats ")
        print("3. PasswordReset Stats")
        print("4. Verification Stats")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            df = setup_pyspark()
            # registration stats
            compute_registration_analysis(df)
            df.sparkSession.stop()
        elif choice == "2":
            #login stats
            compute_login_stats(".\src\python\data_files\logs.txt")
        elif choice == "3":
            #password reset 
            df = setup_pyspark()
            compute_passwordReset_stats(df)
            df.sparkSession.stop()
        elif choice == "4":
            # #verification stats 
            df = setup_pyspark()
            verification_stats_df = compute_verification_stats(df)
            verification_stats_df.show(truncate=False)
            df.sparkSession.stop()
        else:
            print("Exiting")
            break
    
    
    
    
    
    
    
    
    
    
    
    