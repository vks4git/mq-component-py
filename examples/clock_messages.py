from mq.protocol import MessagePack
from msgpack import unpackb

class ClockRequest(MessagePack):
    def __init__(self):
        self.question = "What time is it?"

    def unpack(self, packed_data):
        self.question = unpackb(packed_data, raw=False)['question']

class ClockResponse(MessagePack):
    def __init__(self, time : int = None):
        self.answer = time

    def unpack(self, packed_data):
        self.answer = unpackb(packed_data, raw=False)['answer']

