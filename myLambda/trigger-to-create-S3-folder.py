import json
import boto3
import os

def lambda_handler(event, context):
    
    bucket_name = os.environ['s3_bucket']
    
    # Extract the eventID from the event
    event_id = event['Records'][0]['dynamodb']['Keys']['id']['S']
    
    # Create a folder in the S3 bucket
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=bucket_name, Key=event_id + '/')
     
    for record in event['Records']:
        if record['eventName'] == 'REMOVE':
            # Extract the eventID from the record
            event_id = record['dynamodb']['Keys']['id']['S']
            
            # Check if the bucket has content
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=event_id + '/')
            if 'Contents' in response:
                # Bucket has content, delete the objects first
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
            
            # Delete the folder from the S3 bucket
            s3_client.delete_object(Bucket=bucket_name, Key=event_id + '/')
            
            return {
                'statusCode': 200,
                'body': json.dumps(str(event_id) + ' folder deleted from bucket: ' + str(bucket_name))
            }
    
    return {
        'statusCode': 200,
        'body': json.dumps(str(event_id) + ' folder created in bucket: ' + str(bucket_name))
    }