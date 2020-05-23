import sendgrid
from sendgrid.helpers.mail import *


def send_email(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    request_json = request.json

    sg = sendgrid.SendGridAPIClient(api_key=request_json['api_key'])
    fine_amount = request_json['fine_amount']
    speed = request_json['speed']
    ticket_id = request_json['ticket_id']
    from_email = Email(request_json['from'])
    to_email = To(request_json['to'])
    subject = "You have been served a Speed-Ticket"

    email_message = "Hello, You were overspeeding with speed of {} MPH. This is a notice for a fine of {} ether. You can pay your fine referring to ticketId: {}".format(
        speed, fine_amount, ticket_id)

    content = Content("text/plain", email_message)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)