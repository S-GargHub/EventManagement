import boto3
from datetime import datetime, timedelta

from calendarAPI import get_events


def lambda_handler(event, context):
    # Extract necessary data from the event
    user_id = event['user_id']
    credentials = event['credentials']
    # Call the function to get upcoming events
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    event_list = get_events(credentials, start_date, end_date)
    
    # Send notifications for upcoming events
    send_notifications(event_list)
    return event_list


def send_notifications(event_list):
    # Function to send notifications for events scheduled to happen in the next one hour
    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-west-2:590184108781:upcomingEvents'  # Replace with your actual SNS topic ARN
    
    for event in event_list:
        event_time = datetime.strptime(event['time'], '%Y-%m-%d %H:%M')
        now = datetime.now()
        time_diff = event_time - now

        if time_diff <= timedelta(hours=1):
            message = f"Reminder: {event['id']} -  {event['summary']} is scheduled for {event['time']}"
            attendees = event['attendes']
            for attendee in attendees:
                response = sns.publish(TopicArn=topic_arn, Message=message, MessageAttributes={
                    'attendee': {
                        'DataType': 'String',
                        'StringValue': attendee
                    }
                })
                print(f'Email sent to {attendee}. Message ID: {response["MessageId"]}')