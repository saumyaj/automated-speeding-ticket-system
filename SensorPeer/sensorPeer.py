import sys
import os
import base64
import json
sys.path.append(os.path.realpath('../p2p'))

from btpeer import *

REGSENSOR = 'REGS'

class SensorPeer(BTPeer):

    def __init__(self, maxpeers, serverport, myid=None):
        BTPeer.__init__(self, maxpeers, serverport, myid)

        self.addrouter(self.__router)

        # self.register_to_server()

        # TODO - add handlers if any
        handlers = {
		}
        for mt in handlers:
            self.addhandler(mt, handlers[mt])

    def __router(self, peerid):
        if peerid not in self.getpeerids():
            return (None, None, None)
        else:
            rt = [peerid]
            rt.extend(self.peers[peerid])
            return rt

    def send_image_data(self, data):
        self.sendtopeer('main_server', 'IMGDATA', data)

    def register_to_server(self):
        server_list = self.get_server_list()
        for server in server_list:
            id, ip, port = server
            self.addpeer(id, ip, port)
            print('sending to peer')
            data = {"port": self.serverport}
            response = self.sendtopeer(id, REGSENSOR, json.dumps(data))
            print(response)
            if len(response) > 0:
                if self.debug:
	                btdebug( 'registered successfully!' )

    def get_server_list(self):

        # TODO - call the http function to get registration details
        return [('192.168.0.222:1024', '192.168.0.222', 1024)]