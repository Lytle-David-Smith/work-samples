try:
    # Databricks notebook
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
except ImportError:
    # Local development in VS Code
    from databricks_connect import SparkSession
    spark = SparkSession.builder.getOrCreate()

from databricks.sdk.runtime import dbutils#, spark
from pyspark.sql.types import StructType, StructField, LongType, StringType
from pyspark.sql.functions import from_unixtime, from_utc_timestamp, col, concat, lit, format_number, length, lpad
from datetime import datetime
import pytz
import os

# Define the schema for the DataFrame
fslsSchema = StructType([
    StructField('path', StringType()),
    StructField('name', StringType()),
    StructField('size', LongType()),
    StructField('modificationTime', LongType())
])

def dir(path, timezone=None):
    # Check if the path is a DBFS path or a local path
    if path.startswith('dbfs:'):
        # List the files in the specified DBFS path
        filelist = dbutils.fs.ls(path)
    else:
        # List the files in the specified local path
        filelist = [os.path.join(path, f) for f in os.listdir(path)]
        filelist = [{'path': f, 'name': os.path.basename(f), 'size': os.path.getsize(f), 'modificationTime': int(os.path.getmtime(f)) * 1000} for f in filelist]

    # Time shift based on the specified time zone
    if timezone is None:
        eastern = pytz.timezone('US/Eastern')
        isDST = bool(datetime.now(eastern).dst())
        if isDST:
            timezone = 'EDT'
        else:
            timezone = 'EST'

    if timezone in ['EST', 'CST', 'MST', 'PST']:
        tz_shift_hours = {'EST': 5, 'CST': 6, 'MST': 7, 'PST': 8}[timezone]
        tz_designation = ' ' + timezone
    elif timezone in ['EDT', 'CDT', 'MDT', 'PDT']:
        tz_shift_hours = {'EDT': 4, 'CDT': 5, 'MDT': 6, 'PDT': 7}[timezone]
        tz_designation = ' ' + timezone
    else:
        raise ValueError('Invalid timezone')

    # Create a DataFrame from the file list
    df_files = spark.createDataFrame(filelist, fslsSchema)

    # Convert the modification time to 'yyyy-MM-dd HH:mm:ss' format
    df_files = df_files.drop('path')
    df_files = df_files.withColumn('modificationTime', from_unixtime((col('modificationTime')/1000-(60*60*tz_shift_hours)), 'yyyy-MM-dd HH:mm:ss'))
    df_files = df_files.withColumn('modificationTime', concat(df_files['modificationTime'], lit(tz_designation)))

    # Display the DataFrame
    return df_files

# Call the function with the path and (optionally) time zone.
from dir import dir
display(dir('dbfs:/tmp/david.smith/NPPES/', 'EST'))
