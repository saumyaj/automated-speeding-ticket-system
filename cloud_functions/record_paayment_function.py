import boto3

ACCESS_KEY = "AWS ACCOUNT ACCESS KEY"
SECRET_KEY = "AWS ACCOUNT SECRET KEY"
SESSION_TOKEN = "AWS ACCOUNT SESSION TOKEN"


def record_payment(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    ticketId = request.args.get('ticketId')
    # ticketId = request_json['TicketId']

    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=ACCESS_KEY,
                              aws_session_token=SESSION_TOKEN,
                              aws_secret_access_key=SECRET_KEY,
                              region_name='us-east-1')
    table = dynamodb.Table('Tickets')

    response = table.update_item(
        Key={'TicketId': ticketId},
        AttributeUpdates={'status': {
            'Value': 'complete',
            'Action': 'PUT'
        }},
        ReturnValues="UPDATED_NEW")
