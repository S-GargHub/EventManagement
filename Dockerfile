FROM python:3.9-slim

WORKDIR /app


ENV GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
ENV GOOGLE_CLIENT_JSON=$GOOGLE_CLIENT_JSON
ENV GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
ENV SECRET_KEY=$SECRET_KEY

ENV MONGO_URL=$MONGO_URL
ENV MONGO_DB=$MONGO_DB
ENV MONGO_COLLECTION=$MONGO_COLLECTION

ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID 
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

ENV s3_bucket=$s3_bucket
ENV dynamo_table=$dynamo_table

COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--cert=adhoc"]