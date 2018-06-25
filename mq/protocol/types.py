import msgpack
import json
from datetime import datetime

from mq.config import Config

class Logger:
    def __init__(self, name):
        self._config = Config(name)
        self._name = name

    def write_log(self, logstring, log_type = 'info'):
        current_time = str(datetime.now())
        header = '[' + current_time + ' : ' + self._name + ' : ' + log_type + '] ' 
        with open(self._config.logfile, 'a+') as log:
            log.write(header + logstring + '\n')
        if log_type == 'error':
            print(header + logstring)


class JSON:
    def pack(self):
        """ Creates a JSON string from an instance of this class.

        Returns:
            JSON string.
        """
        return json.dumps(self.__dict__).encode('UTF-8')

    def unpack(self, packed_data : bytes):
        raise NotImplementedError('Unpacking from JSON not implemented.')


class MessagePack:
    def pack(self):
        """ Creates a MessagePack byte sequence from an instance of this class.
        * See MessagePack specification at https://msgpack.org/index.html

        Returns:
            MessagePack byte sequence.
        """
        dictionary = {}
        for k, v in self.__dict__.items():
            dictionary[k] = v
        return msgpack.packb(dictionary, use_bin_type = True)

    def unpack(self, packed_data : bytes):
        raise NotImplementedError('Unpacking from MessagePack not implemented.')


class Message(MessagePack):
    def __init__(self):
        self.id:         str   = None
        self.pid:        str   = None
        self.creator:    str   = None
        self.created_at: int   = None
        self.expires_at: int   = None
        self.spec:       str   = None
        self.type:       str   = None
        self.data:       bytes = None
        self.encrypted:  bool  = None
        self.signature:  bytes = None


    def unpack(self, packed_data):
        """ Creates a Message from MessagePack byte sequence.
        * See Message specification at https://github.com/biocad/mq/blob/develop/doc/PROTOCOL.md
        * See MessagePack specification at https://msgpack.org/index.html

        Args:
            packed_message: packed dictionary with field names as keys and field data as values.

        Returns:
            Message: returns Message if success.

        Raises:
            ValueError: if packed_message is not a dictionary or there are missing some necessary fields.

        """
        dictionary = msgpack.unpackb(packed_data, raw=False)

        self.id         = unpack_field(dictionary, 'id')
        self.pid        = unpack_field(dictionary, 'pid')
        self.creator    = unpack_field(dictionary, 'creator')
        self.created_at = unpack_field(dictionary, 'created_at')
        self.expires_at = unpack_field(dictionary, 'expires_at')
        self.spec       = unpack_field(dictionary, 'spec')
        self.type       = unpack_field(dictionary, 'type')
        self.data       = unpack_field(dictionary, 'data')
        self.encrypted  = unpack_field(dictionary, 'encrypted')
        self.signature  = unpack_field(dictionary, 'signature')


class MonitoringResult(MessagePack):
    def __init__(self):
        self.sync_time: int   = None
        self.name:      str   = None
        self.is_alive:  bool  = None
        self.message:   bytes = None

    def unpack(self, packed_data):
        dictionary = msgpack.unpackb(packed_data, raw=False)

        self.sync_time = unpack_field(dictionary, 'sync_time')
        self.name      = unpack_field(dictionary, 'name')
        self.is_alive  = unpack_field(dictionary, 'is_alive')
        self.message   = unpack_field(dictionary, 'message')

def unpack_field(msg: dict, name: str):
    if name in msg:
        return msg.get(name)
    else:
        raise ValueError('could not unpack field with name ' + name)
