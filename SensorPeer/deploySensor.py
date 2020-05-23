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
    i = 1
    # with open('lamb.jpg', 'rb') as imageStream:
    #     filebytes = bytearray(imageStream.read())

    while i < 4:
        print 'sending msg', i
        filename = str(i) + '.jpeg'
        with open(filename, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
        dic = {"speed": (50 + i * 10), "image_bytes": my_string}
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