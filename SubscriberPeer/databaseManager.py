import boto3
import json
import uuid
import requests
import sys
import os
from google.cloud import storage
sys.path.append(os.path.realpath('../gcloud_creds'))

from CloudData import EMAIL_FUNCTION_URL
from CloudData import SENDGRID_API_KEY

OWNER_INFO_TABLE_NAME = 'OwnerInfo'
aws_access_key_id = 'AWS ACCESS KEY'
aws_secret_access_key = 'AWS SECRET KEY'
aws_session_token = 'AWS SESSION TOKEN'

lambda_client = boto3.client('lambda',
                             aws_access_key_id=aws_access_key_id,
                             aws_session_token=aws_session_token,
                             aws_secret_access_key=aws_secret_access_key,
                             region_name='us-east-1')

dynamodb_resource = boto3.resource('dynamodb',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_session_token=aws_session_token,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name='us-east-1')

owner_table = dynamodb_resource.Table(OWNER_INFO_TABLE_NAME)

gcloud_bucket_client = storage.Client.from_service_account_json(
    '../gcloud_creds/cc2020-storage-api.json')
bucket = gcloud_bucket_client.get_bucket('fast_cars')
BUCKET_URL = 'https://console.cloud.google.com/storage/browser/fast_cars/'


def add_ticket_to_db(json_payload):

    response = lambda_client.invoke(FunctionName="AddTicketLambdaFunction",
                                    InvocationType='Event',
                                    Payload=json_payload)
    print 'Ticket added to database'


def send_email_for_fine(email, ticket_id, speed='60', fine='0.6'):
    data = {
        "from": "saumya259@gmail.com",
        "to": email,
        "api_key": SENDGRID_API_KEY,
        "ticket_id": ticket_id,
        "fine_amount": fine,
        "speed": speed
    }
    response = requests.post(url=EMAIL_FUNCTION_URL, json=data)
    print 'Email notification for fine sent!'


def find_owner_details(license_plate):

    response = owner_table.get_item(Key={'LicensePlate': license_plate})
    item = response['Item']
    email = str(item['email'])
    print 'Owner found! ', email
    return email


def process_fine(license_plate, timestamp, speed, image_url=''):
    email = find_owner_details(license_plate)
    ticket_id = str(uuid.uuid1())
    fine = int(speed) / 100.0
    payload = {}
    payload['Speed'] = str(speed)
    payload['TimeStamp'] = str(timestamp)
    payload['LicensePlate'] = str(license_plate)
    payload['TicketId'] = str(ticket_id)
    payload['ImageLink'] = image_url
    payload['Fine'] = str(fine)

    send_email_for_fine(email, ticket_id, speed, str(fine))
    add_ticket_to_db(json.dumps(payload))


def process_image(filename, speed, timestamp):
    #
    # Storing image to cloud bucket
    blob = bucket.blob(filename)
    with open(filename, 'rb') as photo:
        blob.upload_from_file(photo)

    # Extract license plate number
    response = requests.get('http://localhost:5000/?filename=' + filename)
    license_plate = response.text
    print license_plate
    # initiate fine procedure
    process_fine(license_plate, timestamp, speed, BUCKET_URL + filename)