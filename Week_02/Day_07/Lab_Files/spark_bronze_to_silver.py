from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

spark = SparkSession.builder.appName('BronzeToSilver').getOrCreate()
# Example schema inference omitted for brevity
bronze_df = spark.readStream.format('iceberg').option('path','s3a://bronze/orders_bronze').load()
clean_df = bronze_df.withColumn('event_time_ts', expr('to_timestamp(event_time)')).dropDuplicates(['order_id'])
clean_df.writeStream.format('iceberg').option('checkpointLocation','/tmp/chk/orders_silver').option('path','s3a://silver/orders_silver').outputMode('append').start().awaitTermination()
