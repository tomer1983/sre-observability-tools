import os
import sys
import time
import boto3
import requests
import xmltodict
import logging
import urllib3
from botocore.exceptions import ClientError
from prometheus_client import start_http_server, Gauge


urllib3.disable_warnings()

# store variables from env
bucket_name = os.getenv('BUCKET_NAME', 'bucket_name')
bucket_decription = os.getenv('BUCKET_DECRIPTION' , 'default bucket_decription')
access_key = os.getenv('ACCESS_KEY', 'access_key')
secret_access_key = os.getenv('SECRET_ACCESS_KEY', 'secret_access_key')
endpoint_url = os.getenv('ENDPOINT_URL', 'endpoint_url like prod.tom432.tomer.com')
exporter_version = os.getenv('EXPORTER_VERSION', 'default exporter version')

log_level = 'info'
logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.getLevelName(log_level.upper()))

logging.info('exporter information - version: %s', exporter_version)
logging.info('----------------------------------------')
logging.info('bucket name: %s', bucket_name)
logging.info('bucket decription: %s', bucket_decription)
logging.info('endpoint url: %s', endpoint_url)


# Define the Prometheus metrics
connection_status_metric = Gauge('hcp_connection_status', 'S3 connection status metric (0=unsuccessful, 1=successful)')
bucket_usage_metric = Gauge('hcp_bucket_size_in_use', 'Size of S3 bucket in bytes', ['bucket'])
bucket_free_metric = Gauge('hcp_bucket_size_free', 'Size of S3 bucket in bytes', ['bucket'])
objects_count_metric = Gauge('hcp_objects_count', 'objectCount status metric', ['bucket'])
bucket_size_limit_metric = Gauge('hcp_bucket_size_limit', 'Total size of S3 bucket in bytes', ['bucket'])


s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, endpoint_url="https://"+endpoint_url, verify=False)

def check_connection():
    try:
        s3.head_bucket(Bucket=bucket_name)
        connection_status_metric.set(1)
        logging.info(f"Connection successful to: {bucket_name}")
        print("Connection successful to: {bucket_name}")
    except Exception as e:
        # Handle any other exceptions here
        connection_status_metric.set(0)
        logging.error(f"Unexpected error occurred: {str(e)}")
        print(f"Unexpected error occurred: {str(e)}")



def get_statistics():

    totalCapacityBytes = 0
    usedCapacityBytes = 0
    softQuotaPercent= 0
    objectCount= 0

    try:
        url = f"https://{bucket_name}.{endpoint_url}/proc/statistics"
        payload  = {}
        headers = {
        'Authorization': 'HCP ' + access_key + ':' + secret_access_key,
        'Content-Type': 'application/json',
        'Accept': 'application/xml'
        }
        response = requests.request("GET", url, headers=headers, data = payload, verify=False)
        json_obj = xmltodict.parse(response.text.encode('utf8'))
        
        print(json_obj)
        logging.info(f"json_obj: {json_obj}")

        totalCapacityBytes = int(json_obj['statistics']['@totalCapacityBytes'])
        usedCapacityBytes = int(json_obj['statistics']['@usedCapacityBytes'])
        softQuotaPercent = int(json_obj['statistics']['@softQuotaPercent'])
        objectCount = int(json_obj['statistics']['@objectCount'])

        free_bucket_size_in_bytes = totalCapacityBytes - usedCapacityBytes
        bucket_usage_quota = (usedCapacityBytes/totalCapacityBytes) * 100 if totalCapacityBytes > 0 else 0
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")

    return totalCapacityBytes, usedCapacityBytes, softQuotaPercent, objectCount , free_bucket_size_in_bytes, bucket_usage_quota


if __name__ == '__main__':
    # Start the Prometheus HTTP server
    start_http_server(5000)

    while True:
        logging.info('start scraping')
        check_connection()
        
        #Measure the bucket size, number of entities, and total bucket size, and set the Prometheus metrics
        totalCapacityBytes, usedCapacityBytes, softQuotaPercent, objectCount , free_bucket_size_in_bytes, bucket_usage_quota = get_statistics()


        bucket_usage_metric.labels(bucket_name).set(usedCapacityBytes)
        bucket_free_metric.labels(bucket_name).set(free_bucket_size_in_bytes)
        objects_count_metric.labels(bucket_name).set(objectCount)
        bucket_size_limit_metric.labels(bucket_name).set(bucket_usage_quota)


        logging.info('end scraping')
        # Wait for 1 minute before measuring again
        time.sleep(60)


