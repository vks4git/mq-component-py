from mq.protocol import JSON
from json import loads

class ClockRequest(JSON):
    def __init__(self):
        self.question = "What time is it?"

    def unpack(self, packed_data):
        self.question = loads(packed_data.decode('UTF-8'))['question']

class ClockResponse(JSON):
    def __init__(self, time : int = None):
        self.answer = time

    def unpack(self, packed_data):
        self.answer = loads(packed_data.decode('UTF-8'))['answer']

