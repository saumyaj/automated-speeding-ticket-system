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


aws_access_key_id='ASIA4KHZ3NQ4NIQTD5FP'
aws_secret_access_key='6MdM1CNeZ1ZLuQybIfNo9LWAUkEbk+IWcdvykOYD'
aws_session_token='FwoGZXIvYXdzEP///////////wEaDOrf2AfdMhRva4iiOCK9AUSTfg984aXxBPl3LtDboTTgopzluj43Ib+uhbz75PsMciOn+FJKLVNWH+vQiiQy9t04FF5QXL0/L4hL2iBLMXR8HOp4EV+P00DJqhMsOnu4G85DoRRrY1n37cSIgD3/jStiqUN+bXuy3m5JaRbxqzWQo7cEzD43gNC03JniUtjCDgusegzbKffbdJS9g3PyrPVqaW0O9I0GxCprX+0TNCQi5zJmzRy+lc11UcX8XTI+Jj9IK0Sd8dWXr08oKyjjn5/2BTIt8xmjkUucruAtC6QDV32BFonST+REIgMmwRaKBPkrot+p6HylfaCMiLjHF5SK'

# aws_access_key_id = 'ASIA4KHZ3NQ4P5JC2ZUS'
# aws_secret_access_key = 'eEtzu/2sltcGm5EHil5H7CnsMnM7EFN496WkvXNp'
# aws_session_token = 'FwoGZXIvYXdzEPX//////////wEaDKlbxJ1iXv6ZjmtWtiK9ASNE56oltAdHmA9Vs5aYJAl0vGaPlhEjhTlmCygpzBW5zauzBRaJN5Osl39+yiyrusPXQldJ9RZsYjCPT6Og3IHDQfVk+VjOij2XBFuILmtNJqbiGn99njrxz0oES0It3yctKSMS1cXAQa00JNDVQ8ppfdEdp6OVT1LZhr20enGHTjLuy7xKiG3dIpLKm7OVJarZRcX0X7E695zNhlNgjYZXJTTCkBRTWO+PMkv+bKq8Hx51ewuPfcclmVPC5iiHnJ32BTItsfG7jHyLwPvE4N0pgkZJJ2xL+yccBEtHuegcqC3w4FMu3uAK51VKBUGegtq+'

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


# def update_status():
# ACCESS_KEY = "ASIA4KHZ3NQ4CZO3EDFF"
# SECRET_KEY = "XtGEomqA0FohNS4qfqIVMvuTCb4IQELnTTWYg58h"
# SESSION_TOKEN = "FwoGZXIvYXdzEOb//////////wEaDA7NdurNvfVw2CJg7yK9AZdw0qcyOmaIcYReRmTOxm9GGttJmOpOYvIMGoB6bvAX1OS0yY1i28RSYLvlM7sLUFeW2VgiKk+ORaHRRqAeW3p2hQ2umq8qlyy5dQKnHclToPOZeRrNdIHIZcIgLsLD8iEptD3NN5hL6DnEltJX2QbSH1RvjyRgt7ioSyuUE9gdWTi1k3AFuxCZnUh9c4zZjBJCT8G1mdXcbyc04GutoPm4TSoDt0N8o5/G7FSIvqY3JUf45u46oXIOQD9leyif75n2BTIt2PI/ug78ido8Jh1ZgYTzenYWz0nSZTe+9dJbMF+5gOhuG/mBPRX4ZArpIOfz"

# dynamodb = boto3.resource('dynamodb',
#                           aws_access_key_id=ACCESS_KEY,
#                           aws_session_token=SESSION_TOKEN,
#                           aws_secret_access_key=SECRET_KEY,
#                           region_name='us-east-1')
# table = dynamodb.Table('Tickets')

# response = table.update_item(
#         Key={'TicketId': 'idddddddd'},
#         AttributeUpdates={'status': {
#             'Value': 'finito',
#             'Action': 'PUT'
#         }},
#         ReturnValues="UPDATED_NEW")


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


# process_image()

# process_image('lambo1.jpg', '60', '101010101')

# send_email_for_fine('saumyaj@live.com', '10101', '75', '0.75')