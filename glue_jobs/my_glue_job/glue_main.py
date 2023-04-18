import sys
import random
import boto3

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, functions as f

from utility.utils import get_data

sparkConf = SparkConf().setAppName("GlueJob")\
                    .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")\
                    .set("spark.sql.hive.convertMetastoreParquet", "false")

glueContext = GlueContext(SparkContext.getOrCreate(sparkConf))
spark = glueContext.spark_session     

ssm = boto3.client('ssm')
bucket_name = ssm.get_parameter(Name="/sample-pipeline/bucket-name")['Parameter']['Value']

data_list = []
for i in range(200):
    data_list.append({
        'id': i,
        'rank': random.randrange(200)
    })

df = spark.createDataFrame(data_list).withColumn("ts", f.current_timestamp())

hudi_options = {
    'hoodie.table.name': "tableName",
    'hoodie.datasource.write.recordkey.field': 'id',
    'hoodie.datasource.write.partitionpath.field': 'partitionpath',
    'hoodie.datasource.write.table.name': "tableName",
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'ts',
    'hoodie.upsert.shuffle.parallelism': 2,
    'hoodie.insert.shuffle.parallelism': 2
}

(
    df
    .write
    .mode("overwrite")
    .format("hudi")
    .options(**hudi_options)
    .save(f"s3://{bucket_name}/output_data")
)