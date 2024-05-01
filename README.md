# EventManagement
A web app to manage your calendar events. The Event Management Portal is a web application that allows users to create, manage, update, and view upcoming events. Users can upload event-related images (or other files), view event details, and like their favorite photos locally.

## Technologies Used
- Python Flask for the backend
- HTML, CSS, and JavaScript for the frontend
- AWS S3 for storing images
- AWS DynamoDB for storing event data
- AWS SNS for sending event Notifications
- Google OAuth for user authentication
- FancyBox for image pop-up view effect

## AWS Services Used
- Amazon S3
- AWS SNS
- AWS Lambda
- Amazon DynamoDB
- IAM Roles
- Lambda Functions
- AWS Amplify
- AWS Cognito

## Installation
1. Clone the repository: `git clone https://github.com/CharulRathore/EventManagement.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see below)
4. Create the Lambda functions using scripts from the 'myLambda' folder and set up triggers.
5. Run the application: `flask run`

## Environment Variables
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: The AWS region where your S3 bucket is located
- `S3_BUCKET_NAME`: Create an S3 bucket, set appropriate IAM roles, and add the bucket name here.
- `DYNAMO_METADATA_TABLE`: Create a DynamoDB table, set appropriate IAM roles, and add the table name here.
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
