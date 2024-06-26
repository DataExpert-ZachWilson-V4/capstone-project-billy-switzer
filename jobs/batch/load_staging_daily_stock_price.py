import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, lit, col
from datetime import datetime


args = getResolvedOptions(sys.argv, ["JOB_NAME", "ds", 'output_table', 'polygon_access_key_id', 'polygon_api_key'])
run_date = args['ds']
output_table = args['output_table']
polygon_access_key_id = args['polygon_access_key_id']
polygon_api_key = args['polygon_api_key']

# Create a SparkSession with S3 endpoint configuration
spark = SparkSession.builder \
    .appName("ReadFromS3") \
    .getOrCreate()

glueContext = GlueContext(spark.sparkContext)
spark = glueContext.spark_session


# Define the S3 bucket and access configuration
s3_bucket = "s3a://flatfiles"
spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", polygon_access_key_id)
spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", polygon_api_key)
spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "https://files.polygon.io/")
spark._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

spark.sql(f"""
CREATE OR REPLACE TABLE {output_table} (
    ticker STRING,	
    volume BIGINT,
    open DOUBLE,
    close DOUBLE,
    high DOUBLE,
    low DOUBLE,
    window_start BIGINT,
    transactions BIGINT,
    snapshot_date DATE
)
USING iceberg
PARTITIONED BY (snapshot_date)
""")

run_date_obj = datetime.strptime(run_date, '%Y-%m-%d')

if run_date_obj.weekday() < 5:
    
    year = str(run_date).split('-')[0]
    month = str(run_date).split('-')[1]    

    file_path = f"{s3_bucket}/us_stocks_sip/day_aggs_v1/{year}/{month}/{run_date}.csv.gz"
    df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(file_path)

    # Write the DataFrame to the Iceberg table
    df.withColumn('snapshot_date', from_unixtime(col("window_start")/lit(1000*1000*1000)).cast('date')) \
        .sortWithinPartitions("ticker").writeTo(output_table) \
        .tableProperty("write.spark.fanout.enabled", "true") \
        .overwritePartitions()

job = Job(glueContext)
job.init(args["JOB_NAME"], args)