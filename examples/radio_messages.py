from mq.protocol import JSON
from json import loads

class RadioMessage(JSON):
    def __init__(self):
        self.message = "Hello! It's me."

    def unpack(self, packed_data):
        self.message = loads(packed_data.decode('UTF-8'))['message']
