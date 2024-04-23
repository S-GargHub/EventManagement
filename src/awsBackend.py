import boto3

# Insert event metadata into DynamoDB
def put_event_metadata_dynamodb(event, summary, start_date, end_date):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Calendar_Event_Metadata')
    table.put_item(
        Item={
            'summary': summary,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'id': event['id'],
        }
    )


# Delete the metadata from DynamoDB
def delete_event_dynamodb(event_id):    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Calendar_Event_Metadata')
    table.delete_item(
        Key={
            'id': event_id
        }
    )


# Check if an event folder exist in S3 bucket
def find_event_s3(event_id):
    s3 = boto3.client('s3')
    s3_bucket_name = 'calender-app-bucket'

    response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=event_id+'/')
    
    if 'Contents' in response:
        return True
    return False


# Upload file to S3 folder
def upload_file_S3(file, event_id):
    s3 = boto3.client('s3')
    s3_bucket_name = 'calender-app-bucket'

    try:
        s3.upload_fileobj(file, s3_bucket_name , f'{event_id}/{file.filename}')
    except Exception as e:
        return e