import multiprocessing

from messageServerPeer import *


def start_mainloop(peer):
    peer.mainloop()


def initialize(peer):
    peer.register_to_server()


def main():
    peer = MessageServerPeer(10, 1024, debug=0)
    p1 = multiprocessing.Process(target=start_mainloop, args=(peer, ))
    p2 = multiprocessing.Process(target=initialize, args=(peer, ))

    p1.start()
    p2.start()

    p2.join()
    print 'process 2 finished execution!'


if __name__ == "__main__":
    main()