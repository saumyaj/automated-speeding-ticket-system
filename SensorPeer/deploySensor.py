import multiprocessing
import time
import base64

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
    # with open('lamb.jpg', 'rb') as imageStream:
    #     filebytes = bytearray(imageStream.read())

    with open("lamb.jpg", "rb") as img_file:
        my_string = base64.b64encode(img_file.read())

    while i < 10:
        print 'sending msg', i
        dic = {"speed": (100 + i), "image_bytes": my_string}
        peer.publish_message(json.dumps(dic))
        i += 1
        time.sleep(2)


def main():
    peer = SensorPeer(10, 1025, debug=0)
    p1 = multiprocessing.Process(target=start_mainloop, args=(peer, ))
    p2 = multiprocessing.Process(target=simulate, args=(peer, ))

    p1.start()
    p2.start()

    p2.join()
    print 'process 2 finished execution!'


if __name__ == "__main__":
    main()