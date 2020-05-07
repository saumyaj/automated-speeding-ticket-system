import multiprocessing
import time

from sensorPeer import *


def start_mainloop(peer):
    peer.mainloop()


def initialize(peer):
    peer.register_to_server()


def simulate(peer):
    initialize(peer)
    send_messages(peer)


def send_messages(peer):
    i = 0
    while i < 10:
        print 'sending msg', i
        dic = {"speed": (100 + i)}
        peer.publish_message(json.dumps(dic))
        i += 1
        time.sleep(2)


def main():
    peer = SensorPeer(10, 1025, debug=0)
    initialize(peer)
    p1 = multiprocessing.Process(target=start_mainloop, args=(peer, ))
    p2 = multiprocessing.Process(target=simulate, args=(peer, ))

    p1.start()
    p2.start()

    p2.join()
    print 'process 2 finished execution!'


if __name__ == "__main__":
    main()