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


# gell all the image file from S3 folder to dashboard
def get_s3_content(event_id):
    s3 = boto3.client('s3')
    bucket_name = 'calender-app-bucket'
    prefix = f'{event_id}/' 

    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        s3_content = []
        for item in response.get('Contents', []):
            key = item['Key']
            if not key.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                continue  # Skip non-image files
            # Generate a pre-signed URL for each object 
            url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=3600)
            # Extract the filename from the object key
            filename = key.split('/')[-1]
            s3_content.append({'url': url, 'name': filename})

        return s3_content
    except Exception as e:
        print(f"Failed to fetch S3 content: {e}")
        return []