from mq.protocol.types import JSON
import msgpack

class MQError(JSON):
    def __init__(self, code : int = None, message : str = None):
        self.code = code
        self.message = message

    def unpack(self, packed_data):
        dictionary = msgpack.unpackb(packed_data, raw=False)

        self.code    = unpack_field(dictionary, 'code')
        self.message = unpack_field(dictionary, 'message')

# Error codes

# PROTOL ERROR: 1xx
########################################

error_protocol : int = 100

error_encoding : int = 101

########################################
# TRANSPORT ERROR: 2xx
########################################

error_transport : int = 200

error_tag : int = 201

########################################
# TECHNICAL ERROR: 3xx
########################################

error_technical : int = 300

error_killed : int = 301

########################################
# COMPONENT ERROR: 5xx
########################################

error_component : int = 500

error_foreign : int = 501
