from mq.protocol import MessagePack
from msgpack import unpackb

class BankRequest(MessagePack):
    def __init__(self, monthly : float = None, months : int = None):
        self.per_month = monthly
        self.months = months

    def unpack(self, packed_data):
        data = unpackb(packed_data, raw=False)
        self.per_month = data['per_month']
        self.months = data['months']

class BankResponse(MessagePack):
    def __init__(self, res : float = None):
        self.answer = res

    def unpack(self, packed_data):
        data = unpackb(packed_data, raw=False)
        self.answer = data['answer']
