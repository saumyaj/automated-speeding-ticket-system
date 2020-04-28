import sys
import os
import base64
import json
sys.path.append(os.path.realpath('../p2p'))

from networkPeer import *

#Sending message Types
PULLIMG = 'PULL'  # pull images request
REGSUB = 'RSUB'  # Registing the subscriber

#Receiving message types
DATA = 'DATA'  # Sending pulled data from cloud

#Receiving response (not the message) types
ACKOK = 'ACKO'
NACK = 'NACK'
ACKPULL = 'ACKP'  # Achknowledge pull req


class SubscriberPeer(NetworkPeer):
    def __init__(self, maxpeers, serverport, myid=None, debug=0):
        NetworkPeer.__init__(self,
                             maxpeers,
                             serverport,
                             PeerType.SUBSCRIBER,
                             myid,
                             debug=debug)

        # TODO - add handlers if any
        handlers = {DATA: self.handle_pulled_data}
        self.add_handlers(handlers)

    def register_to_server(self):
        server_list = self.get_server_list_dict()
        for server in server_list:
            id, host, port = server

            # First try to register with the core
            print host, port
            responses = self.connectandsend(host, port, REGSUB,
                                            json.dumps(self.identification))
            if len(responses) > 0:
                msgtype, msg = responses[0]
                if msgtype == ACKOK:
                    self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
                    print 'subscriber has registered successfully'
                elif msgtype == NACK:
                    # Ask for the list
                    res = self.connectandsend(host, port, SRVRLSTREQ, '')
                    _, msg = res[0]
                    if try_connecting_once(json.loads(msg)):
                        break
                else:
                    print 'Unknown msgtype response!'
            else:
                print 'No response!'

    def try_connecting_once(self, peerlist):
        for peer in peerlist:
            id, host, port = peer
            responses = self.connectandsend(host, port, REGSUB, '')
            if len(responses) > 0:
                msgtype, msg = responses[0]
                if msgtype == ACKOK:
                    self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
                    return True
        return False

    def get_server_list_dict(self):

        # TODO - call the http function to get registration details
        return [('192.168.0.222:1024', '192.168.0.222', 1024)]

    def get_new_data_to_process(self, qty=5):
        recipient_id = self.get_peer_ids(PeerType.MESSAGESERVER)[0]
        print('getting new data from ', recipient_id)
        datadict = {}
        datadict['qty'] = qty
        datadict['address'] = self.myid
        res = self.sendtopeer(recipient_id, PULLIMG, json.dumps(datadict))
        print(res)


    def save_image_to_jpg(image_bytes, filename):
        pass

    def call_detection_process(filename):
        anpr_dir = ''
        os.system('./detector_script.sh ' + anpr_dir + ' ' + filename)

    def handle_pulled_data(self, peerconn, data):
        # TODO - Call the image processing services
        print 'data handler invoked!'
        datadict = json.loads(data)
        for d in datadict:
            di = json.loads(d)
            print di['speed']
            filename = 'image.jpg'
            save_image_to_jpg(di['image'], filename)
            call_detection_process(filename)



