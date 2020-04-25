import multiprocessing
import time

from subscriberPeer import *


def start_mainloop(peer):
    peer.mainloop()


def initialize(peer):
    peer.register_to_server()


def simulate(peer):
    initialize(peer)
    get_images(peer)


def get_images(peer):

    i = 0
    while i < 10:
        peer.get_new_data_to_process()
        i += 1
        time.sleep(2)


def main():
    peer = SubscriberPeer(10, 1026, debug=0)
    p1 = multiprocessing.Process(target=start_mainloop, args=(peer, ))
    p2 = multiprocessing.Process(target=simulate, args=(peer, ))

    p1.start()
    p2.start()

    p2.join()
    print 'process 2 finished execution!'


if __name__ == "__main__":
    main()