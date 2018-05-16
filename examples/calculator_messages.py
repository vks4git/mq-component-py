from mq.protocol import JSON
import json

class CalcRequest(JSON):
    def __init__(self, op1 : float = None, op2 : float = None, act : str = None):
        self.first = op1
        self.second = op2
        self.action = act

    def unpack(self, packed_data):
        data = json.loads(packed_data.decode('UTF-8'))
        self.first = data['first']
        self.second = data['second']
        self.action = data['action']

class CalcResponse(JSON):
    def __init__(self, res : float = None):
        self.answer = res

    def unpack(self, packed_data):
        data = json.loads(packed_data.decode('UTF-8'))
        self.answer = data['answer']
