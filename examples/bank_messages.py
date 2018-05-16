from mq.protocol import JSON
import json

class BankRequest(JSON):
    def __init__(self, monthly : float = None, months : int = None):
        self.per_month = monthly
        self.months = months

    def unpack(self, packed_data):
        data = json.loads(packed_data.decode('UTF-8'))
        self.per_month = data['per_month']
        self.months = data['months']

class BankResponse(JSON):
    def __init__(self, res : float = None):
        self.answer = res

    def unpack(self, packed_data):
        data = json.loads(packed_data.decode('UTF-8'))
        self.answer = data['answer']
