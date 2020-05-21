import boto3
import json
import uuid
import requests
import sys
import os
sys.path.append(os.path.realpath('../gcloud_creds'))

from CloudData import EMAIL_FUNCTION_URL
from CloudData import SENDGRID_API_KEY

OWNER_INFO_TABLE_NAME = 'OwnerInfo'

lambda_client = boto3.client('lambda', region_name='us-east-1')
dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
owner_table = dynamodb_resource.Table(OWNER_INFO_TABLE_NAME)


def add_ticket_to_db(json_payload):

    response = lambda_client.invoke(FunctionName="AddTicketLambdaFunction",
                                    InvocationType='Event',
                                    Payload=json_payload)


def send_email_for_fine(email):
    data = {
        "from": "saumya259@gmail.com",
        "to": email,
        "api_key": SENDGRID_API_KEY,
    }
    response = requests.post(url=EMAIL_FUNCTION_URL, json=data)
    print response.text


def find_owner_details(license_plate):

    response = owner_table.get_item(Key={'LicensePlate': license_plate})
    item = response['Item']
    email = str(item['email'])
    return email


def process_fine(license_plate, timestamp, speed, image_string=''):
    email = find_owner_details(license_plate)
    ticket_id = uuid.uuid1()
    payload = {}
    payload['Speed'] = str(speed)
    payload['TimeStamp'] = str(timestamp)
    payload['LicensePlate'] = str(license_plate)
    payload['TicketId'] = str(ticket_id)
    payload['ImageLink'] = image_string

    send_email_for_fine(email)
    add_ticket_to_db(json.dumps(payload))


def update_status():
    ACCESS_KEY = "ASIA4KHZ3NQ4CZO3EDFF"
    SECRET_KEY = "XtGEomqA0FohNS4qfqIVMvuTCb4IQELnTTWYg58h"
    SESSION_TOKEN = "FwoGZXIvYXdzEOb//////////wEaDA7NdurNvfVw2CJg7yK9AZdw0qcyOmaIcYReRmTOxm9GGttJmOpOYvIMGoB6bvAX1OS0yY1i28RSYLvlM7sLUFeW2VgiKk+ORaHRRqAeW3p2hQ2umq8qlyy5dQKnHclToPOZeRrNdIHIZcIgLsLD8iEptD3NN5hL6DnEltJX2QbSH1RvjyRgt7ioSyuUE9gdWTi1k3AFuxCZnUh9c4zZjBJCT8G1mdXcbyc04GutoPm4TSoDt0N8o5/G7FSIvqY3JUf45u46oXIOQD9leyif75n2BTIt2PI/ug78ido8Jh1ZgYTzenYWz0nSZTe+9dJbMF+5gOhuG/mBPRX4ZArpIOfz"

    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=ACCESS_KEY,
                              aws_session_token=SESSION_TOKEN,
                              aws_secret_access_key=SECRET_KEY,
                              region_name='us-east-1')
    table = dynamodb.Table('Tickets')

    response = table.update_item(
        Key={'TicketId': 'idddddddd'},
        AttributeUpdates={'status': {
            'Value': 'finito',
            'Action': 'PUT'
        }},
        ReturnValues="UPDATED_NEW")


# process_fine('abc', '33:40', 100, 'some_image')

update_status()