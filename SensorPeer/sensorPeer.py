import sys
import os
import base64
import json
sys.path.append(os.path.realpath('../p2p'))

from networkPeer import *

# Sengin message types
REGSENSOR = 'REGS'  # Register sensor
PUBIMG = 'PIMG'  # publishing image
SRVRLSTREQ = 'SLST'  # ask for messageserver list

#Receiving response (not the message) types
ACKOK = 'ACKO'
NACK = 'NACK'
SRVRLSTRES = 'MLST'
ACKDATA = 'DACK'


class SensorPeer(NetworkPeer):
    def __init__(self, maxpeers, serverport, myid=None, debug=0):
        NetworkPeer.__init__(self,
                             maxpeers,
                             serverport,
                             PeerType.SENSOR,
                             myid,
                             debug=debug)

        # TODO - add handlers if any
        handlers = {}
        self.add_handlers(handlers)

    def send_image_data(self, data):
        self.sendtopeer('main_server', 'IMGDATA', data)

    def register_to_server(self):
        # print 'called!'
        server_list = self.get_server_list()
        print server_list
        for server in server_list:

            id, host, port = server
            # print id
            # First try to register with the core
            responses = self.connectandsend(host, port, REGSENSOR,
                                            json.dumps(self.identification))
            if len(responses) > 0:
                msgtype, msg = responses[0]
                if msgtype == ACKOK:
                    self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
                    print 'registration with a message server successful'
                elif msgtype == NACK:
                    # Ask for the list
                    res = self.connectandsend(host, port, SRVRLSTREQ, '')
                    _, msg = res[0]
                    if self.try_connecting_once(json.loads(msg)):
                        break
                else:
                    print 'Unknown msgtype response!'
            else:
                print 'No response!'

    def try_connecting_once(self, peerlist):
        for peer in peerlist:
            id, host, port = peer
            responses = self.connectandsend(host, port, REGSENSOR,
                                            json.dumps(self.identification))
            if len(responses) > 0:
                msgtype, msg = responses[0]
                if msgtype == ACKOK:
                    self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
                    return True
        return False

    def publish_message(self, msg):
        recipient_id = self.get_peer_ids(PeerType.MESSAGESERVER)[0]
        print('sending message to ', recipient_id)
        res = self.sendtopeer(recipient_id, PUBIMG, msg)
        print(res)