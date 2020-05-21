import sys
import os
import base64
import json
import cv2
import time
import subprocess

sys.path.append(os.path.realpath('../p2p'))

from networkPeer import *

#Sending message Types
PULLIMG = 'PULL'  # pull images request
REGSUB = 'RSUB'  # Registing the subscriber
SRVRLSTREQ = 'SLST'

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
        server_list = self.get_server_list()
        for server in server_list:
            id, host, port = server

            responses = self.connectandsend(host, port, REGSUB,
                                            json.dumps(self.identification))
            if len(responses) > 0:
                msgtype, msg = responses[0]
                if msgtype == ACKOK:
                    self.add_typed_peer(id, host, port, PeerType.MESSAGESERVER)
                    print 'subscriber has registered successfully'
                elif msgtype == NACK:
                    # Ask for the list
                    print 'subscriber has been denied the registration!'
                    res = self.connectandsend(host, port, SRVRLSTREQ, '')
                    _, msg = res[0]
                    print 'trying to connect to a different node!'
                    if self.try_connecting_once(json.loads(msg)):
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

    def get_new_data_to_process(self, qty=5):
        recipient_id = self.get_peer_ids(PeerType.MESSAGESERVER)[0]
        print('getting new data from ', recipient_id)
        datadict = {}
        datadict['qty'] = qty
        datadict['address'] = self.myid
        res = self.sendtopeer(recipient_id, PULLIMG, json.dumps(datadict))
        print(res)

    def save_image_to_jpg(file_bytes, filename):
        file_numpy = numpy.asarray(file_bytes, dtype=numpy.uint8)
        img_data_ndarray = cv2.imdecode(file_numpy, cv2.IMREAD_COLOR)
        cv2.imwrite(filename, img_data_ndarray)

    def call_detection_process(filename):
        result = subprocess.run(['./detector_script.sh', filename],
                                stdout=subprocess.PIPE)
        license_number = result.stdout.decode('utf-8')
        return license_number

    def handle_pulled_data(self, peerconn, data):
        # TODO - Call the image processing services
        print 'data handler invoked!'
        datadict = json.loads(data)
        for d in datadict:
            json_data = json.loads(d)
            print json_data['speed']
            img_data = json_data['image_bytes']
            time_integer = int(time.time() * 1e6)
            filename = str(time_integer) + '.jpg'
            with open(filename, "wb") as fh:
                fh.write(img_data.decode('base64'))

            license_number = call_detection_process(filename)
            print 'yayyy!', license_number