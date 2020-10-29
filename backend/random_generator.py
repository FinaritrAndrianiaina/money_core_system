import time
import os
import binascii


def get_random():
    return binascii.b2a_base64(os.urandom(64)).decode('utf-8')

SIGNATURE = get_random()

def rebuild_signature():
    global SIGNATURE
    while True:
        time.sleep(600)
        SIGNATURE = get_random()



