from mq.protocol import MessagePack
from msgpack import unpackb

class CalcRequest(MessagePack):
    def __init__(self, op1 : float = None, op2 : float = None, act : str = None):
        self.first = op1
        self.second = op2
        self.action = act

    def unpack(self, packed_data):
        data = unpackb(packed_data, raw=False)
        self.first = data['first']
        self.second = data['second']
        self.action = data['action']

class CalcResponse(MessagePack):
    def __init__(self, res : float = None):
        self.answer = res

    def unpack(self, packed_data):
        data = unpackb(packed_data, raw=False)
        self.answer = data['answer']
