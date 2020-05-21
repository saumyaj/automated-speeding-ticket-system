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
SRVRLSTREQ = 'SLST'  # Return active msg server list

#Receiving response (not the message) types
ACKOK = 'ACKO'
NACK = 'NACK'

# Sending response types
ACKDATA = 'DACK'
ACKPULL = 'ACKP'  # Achknowledge pull req

# Maximum peers of each type
# TODO add to the constructor??
MAXSENSORPEERS = 100
MAXSUBSCRIBERPEERS = 100


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
            REGMSGSRVR: self.handle_message_server_registration,
            SRVRLSTREQ: self.handle_server_list_request
        }
        self.add_handlers(handlers)

        self.publisher = pubsub_v1.PublisherClient.from_service_account_json(
            '../gcloud_creds/cc2020-project2-5f202554f621.json')
        self.topic_name = 'projects/cc2020-project2/topics/plates'

        self.subscriber = pubsub_v1.SubscriberClient.from_service_account_json(
            '../gcloud_creds/cc2020-project2-5f202554f621.json')
        self.subscription_path = self.subscriber.subscription_path(
            'cc2020-project2', 'plates')

        self.max_sensors = MAXSENSORPEERS
        self.max_subscribers = MAXSUBSCRIBERPEERS

    def register_to_server(self):
        server_list = self.get_server_list()
        for server in server_list:
            id, host, port = server
            if self.myid == id:
                print 'Booting up core server!'
                return

        for server in server_list:
            id, host, port = server
            if id == self.myid:
                continue
            res = self.connectandsend(host, port, REGMSGSRVR,
                                      json.dumps(self.identification))
            msgtype, _ = res[0]
            if msgtype == ACKOK:
                self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
                print 'Registration with the core msg server successful!'

    def reg_self_as_core(self):
        # TODO - send http func req to add self as core
        pass

    def get_and_send_images_from_subscription(self, peer_id, qty):
        # The subscriber pulls a specific number of messages.
        response = self.subscriber.pull(self.subscription_path,
                                        max_messages=qty)

        ack_ids = []
        data = []
        for received_message in response.received_messages:
            # print("Received: {}".format(received_message.message.data))
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

    # TODO - Test limit number of sensors allowed to register
    def handle_sensor_registration(self, peerconn, data):
        number_of_registered_sensors = len(
            self.typed_peerlist.get(PeerType.SENSOR.name, {}))
        print 'reg sensors: ', number_of_registered_sensors
        if number_of_registered_sensors == self.max_sensors:
            peerconn.senddata(NACK, '')
            return

        datadict = json.loads(data)
        id = datadict['id']
        host = datadict['host']
        port = datadict['port']
        self.add_typed_peer(id, host, port, PeerType.SENSOR)
        peerconn.senddata(ACKOK, '')

    # TODO - Test limit number of subscribers allowed to register
    def handle_subscriber_registration(self, peerconn, data):
        number_of_registered_subscribers = len(
            self.typed_peerlist.get(PeerType.SUBSCRIBER.name, {}))
        if number_of_registered_subscribers == self.max_subscribers:
            peerconn.senddata(NACK, '')
            return

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

    def handle_server_list_request(self, peerconn, data):
        print 'server list req received!'
        server_list_dict = self.typed_peerlist.get(PeerType.MESSAGESERVER.name,
                                                   {})
        server_list = []
        for key in server_list_dict.keys():
            ip, port = server_list_dict[key]
            server_list.append((key, ip, port))
        print server_list
        peerconn.senddata('XXXX', json.dumps(server_list))