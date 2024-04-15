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