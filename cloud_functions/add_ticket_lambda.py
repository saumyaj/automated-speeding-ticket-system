import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Tickets')


def lambda_handler(event, context):

    table.put_item(
        Item={
            "TicketId": event['TicketId'],
            "Speed": event['Speed'],
            "ImageLink": event['ImageLink'],
            "TimeStamp": event['TimeStamp'],
            "LicensePlate": event['LicensePlate'],
            "Fine": event['Fine'],
            "status": "pending"
        })

    return {'statusCode': 200, 'body': 'all good!'}
