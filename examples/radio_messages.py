from mq.protocol import MessagePack
from msgpack import unpackb

class RadioMessage(MessagePack):
    def __init__(self):
        self.message = "".join([chr(x % 256) for x in range(0, 10000000)])

    def unpack(self, packed_data):
        self.message = unpackb(packed_data, raw=False)['message']
