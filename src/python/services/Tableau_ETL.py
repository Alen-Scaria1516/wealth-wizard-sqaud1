import boto3
import time

def Tableau_ETL_utility():
    # 1. Upload a file to S3

    s3_client = boto3.client("s3")

    bucket_name = "glue-usage-as-94"
    local_file = "logs.json"
    s3_key_input = "input/logs.json"
    s3_key_output = "output/transformed_file.csv"

    # Upload file
    s3_client.upload_file(local_file, bucket_name, s3_key_input)
    print(f"Uploaded {local_file} to s3://{bucket_name}/{s3_key_input}")

    # 2. Trigger Glue ETL Job
    glue_client = boto3.client("glue")

    job_name = "MyETL"

    response = glue_client.start_job_run(JobName=job_name)
    job_run_id = response["JobRunId"]
    print(f"Triggered Glue job {job_name}, JobRunId: {job_run_id}")

    # Wait for Glue job to finish
    while True:
        status = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)
        state = status["JobRun"]["JobRunState"]
        print(f"Glue Job State: {state}")
        
        if state in ["SUCCEEDED", "FAILED", "STOPPED"]:
            break
        time.sleep(30)

    if state != "SUCCEEDED":
        raise Exception(f"Glue job failed with state: {state}")
    
    # Athena client
    athena_client = boto3.client("athena", region_name="us-east-1")  # change region if needed

    # Config
    database = "mydb"
    output_s3 = "s3://glue-usage-as-94/athena_results/"   # Athena stores query results here
    s3_data_location = "s3://glue-usage-as-94/output/csv_output/"          # Where your transformed CSVs are
    create_db_query = f"CREATE DATABASE IF NOT EXISTS {database}"

    response = athena_client.start_query_execution(
        QueryString=create_db_query,
        ResultConfiguration={"OutputLocation": output_s3}
    )
    query_execution_id = response["QueryExecutionId"]

    # Wait until DB is created
    while True:
        status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(2)

    if state != "SUCCEEDED":
        raise Exception(f"DB creation failed: {state}")


    # Step 2. Create table
    create_table_query = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {database}.verification_logs (
    email_id STRING,
    category STRING,
    action STRING,
    attempt_number INT,
    status STRING,
    timestamp STRING
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
    WITH SERDEPROPERTIES (
    "separatorChar" = ",",
    "quoteChar"     = '\"'
    )
    LOCATION '{s3_data_location}'
    TBLPROPERTIES ('skip.header.line.count'='1');
    """

    response = athena_client.start_query_execution(
        QueryString=create_table_query,
        ResultConfiguration={"OutputLocation": output_s3}
    )

    query_execution_id = response["QueryExecutionId"]
    print(f"Started Athena CREATE TABLE. Execution ID: {query_execution_id}")

