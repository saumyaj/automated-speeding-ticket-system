import sys
import os
import base64
import json
sys.path.append(os.path.realpath('../p2p'))

from google.cloud import pubsub_v1

from networkPeer import *

#Sending message Types
REGSERVER = 'REGM'  #REGister Messageserver
ACKREG = 'ACKR'  # Acknowledge registration
DATA = 'DATA'  # Sending pulled data from cloud
REGMSGSRVR = 'RSVR'  # REGISTER MESSAGE SERVER with other message servers

#Receiving message types
PUBIMG = 'PIMG'  # publish image request
REGSENSOR = 'REGS'  #Register sensor
PULLIMG = 'PULL'  # pull images request
REGSUB = 'RSUB'  # Registing the subscriber
REGMSGSRVR = 'RSVR'  # REGISTER MESSAGE SERVER with other message servers

#Receiving response (not the message) types
ACKOK = 'ACKO'
NACK = 'NACK'

# Sending response types
ACKDATA = 'DACK'
ACKPULL = 'ACKP'  # Achknowledge pull req


class MessageServerPeer(NetworkPeer):
    def __init__(self, maxpeers, serverport, myid=None, debug=0):
        NetworkPeer.__init__(self,
                             maxpeers,
                             serverport,
                             PeerType.MESSAGESERVER,
                             myid,
                             debug=debug)

        # TODO - add handlers if any
        handlers = {
            PUBIMG: self.handle_publish_request,
            REGSENSOR: self.handle_sensor_registration,
            REGSUB: self.handle_subscriber_registration,
            PULLIMG: self.handle_pull_image_request,
            REGMSGSRVR: self.handle_message_server_registration
        }
        self.add_handlers(handlers)

        self.publisher = pubsub_v1.PublisherClient.from_service_account_json(
            '../gcloud_creds/cc2020-project2-5f202554f621.json')
        self.topic_name = 'projects/cc2020-project2/topics/plates'

        self.subscriber = pubsub_v1.SubscriberClient.from_service_account_json(
            '../gcloud_creds/cc2020-project2-5f202554f621.json')
        self.subscription_path = self.subscriber.subscription_path(
            'cc2020-project2', 'plates')

    def register_to_server(self):

        # TODO - fix this for registration process with cloud function
        # temporarily make self a core node
        print self.myid
        if self.myid == '192.168.0.222:1024':
            print 'id matched!'
            return
        else:
            print 'id not matched!'

            return

        server_list = self.get_server_list()
        if len(server_list) == 0:
            reg_self_as_core()
        else:
            for server in server_list:
                id, host, port = server
                if id == self.myid:
                    continue
                res = self.connectandsend(host, port, REGMSGSRVR,
                                          json.dumps(self.identification))
                msgtype, _ = res[0]
                if msgtype == ACKOK:
                    self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)

    def reg_self_as_core(self):
        # TODO - send http func req to add self as core
        pass

    def get_server_list(self):

        # TODO - call the http function to get registration details
        return [('192.168.0.222:1026', '192.168.0.222', 1026)]

    def get_and_send_images_from_subscription(self, peer_id, qty):
        # The subscriber pulls a specific number of messages.
        response = self.subscriber.pull(self.subscription_path,
                                        max_messages=qty)

        ack_ids = []
        data = []
        for received_message in response.received_messages:
            print("Received: {}".format(received_message.message.data))
            data.append(received_message.message.data)
            ack_ids.append(received_message.ack_id)

        # Acknowledges the received messages so they will not be sent again.
        self.subscriber.acknowledge(self.subscription_path, ack_ids)

        print 'sending to peer:', peer_id
        res = self.sendtopeer(peer_id, DATA, json.dumps(data))
        print 'got the following reponse for the sent data!'
        print res

    def handle_publish_request(self, peerconn, data):
        print('data being handled!')
        # datadict = json.loads(data)
        peerconn.senddata(ACKDATA, '')
        self.publisher.publish(self.topic_name, data)

    def handle_pull_image_request(self, peerconn, data):
        datadict = json.loads(data)
        qty = datadict.get('qty', 1)
        peer_id = datadict['address']
        peerconn.senddata(ACKPULL, 'Request Received!')
        self.get_and_send_images_from_subscription(peer_id, qty)

    # TODO - limit number of sensors allowed to register
    def handle_sensor_registration(self, peerconn, data):
        datadict = json.loads(data)
        id = datadict['id']
        host = datadict['host']
        port = datadict['port']
        self.add_typed_peer(id, host, port, PeerType.SENSOR)
        peerconn.senddata(ACKOK, '')

    # TODO - limit number of subscribers allowed to register
    def handle_subscriber_registration(self, peerconn, data):
        datadict = json.loads(data)
        id = datadict['id']
        host = datadict['host']
        port = datadict['port']
        self.add_typed_peer(id, host, port, PeerType.SUBSCRIBER)
        peerconn.senddata(ACKOK, '')

    def handle_message_server_registration(self, peerconn, data):
        datadict = json.loads(data)
        id = datadict['id']
        host = datadict['host']
        port = datadict['port']
        self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
        peerconn.senddata(ACKOK, '')