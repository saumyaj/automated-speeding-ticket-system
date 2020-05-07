import sys
import os
import base64
import json
import requests
from enum import Enum
sys.path.append(os.path.realpath('../p2p'))
sys.path.append(os.path.realpath('../gcloud_creds'))

from btpeer import *
from CloudData import CLOUD_FUNCTION_URL

#sending Message type for registration messages
REGMSG = 'RGST'  # REGISTER


class PeerType(Enum):
    SENSOR = 1
    MESSAGESERVER = 2
    SUBSCRIBER = 3


class NetworkPeer(BTPeer):
    def __init__(self, maxpeers, serverport, my_type, myid=None, debug=0):
        BTPeer.__init__(self, maxpeers, serverport, myid, debug=debug)

        self.identification = {
            'id': self.myid,
            'host': self.serverhost,
            'port': self.serverport
        }
        try:
            if isinstance(my_type, PeerType):
                self.my_type = my_type
            else:
                raise Exception('peer type must be of type PeerType')
        except Exception:
            # TODO - propagate exception
            print 'exception was thrown'

        self.addrouter(self.__router)

        self.typed_peerlist = {}

    def __router(self, peerid):
        if peerid not in self.getpeerids():
            return (None, None, None)
        else:
            rt = [peerid]
            rt.extend(self.peers[peerid])
            return rt

    def add_handlers(self, handler_dict):
        for mt in handler_dict:
            self.addhandler(mt, handler_dict[mt])

    def add_typed_peer(self, peerid, host, port, peerType):
        peerTypeName = str(peerType.name)
        peer_dict = self.typed_peerlist.get(peerTypeName, {})
        peer_dict[peerid] = (host, int(port))
        self.typed_peerlist[peerTypeName] = peer_dict
        self.addpeer(peerid, host, port)

    def get_peer_ids(self, peerType):
        peerTypeName = str(peerType.name)
        peer_dict = self.typed_peerlist.get(peerTypeName, {})
        return peer_dict.keys()

    def get_server_list(self):
        try:
            r = requests.get(url=CLOUD_FUNCTION_URL, params={})
            data = r.json()
            ip = data['ip']
            ip = ip.encode('ascii', 'ignore')
            port = data['port']
        except:
            print 'exception!'
        return [(ip + ':' + str(port), ip, int(port))]
