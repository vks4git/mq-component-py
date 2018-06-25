from mq.protocol import MessagePack
from msgpack import unpackb

class RadioMessage(MessagePack):
    def __init__(self):
        self.message = "Hello! It's me."

    def unpack(self, packed_data):
        self.message = unpackb(packed_data, raw=False)['message']
