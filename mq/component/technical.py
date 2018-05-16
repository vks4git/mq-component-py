import zmq
import msgpack
from mq.protocol.types import Message
from mq.protocol.tag import message_type, message_spec
import json


def default_tech_listener(config, master_send):
    """
    Technical level dispatcher.
    Receives kill messages and sends kill_task_id to the master thread.
    There this value is compared with current task_id and communication process is restarted if comparison succeeded.
    """
    context = zmq.Context()
    channel = context.socket(zmq.SUB)
    channel.setsockopt(zmq.SUBSCRIBE, b'')
    channel.connect("tcp://" + config.scheduler_out['host'] + ':' + str(config.scheduler_out['techport']))

    while True:
        packed_tag, packed_message = channel.recv_multipart()
        tag = msgpack.unpackb(packed_tag)
        message = Message()
        message.unpack(packed_message)

        msg_type = message_type(tag)
        msg_spec = message_spec(tag)
        if msg_type == 'config' and msg_spec == 'kill':
            master_send.send(json.loads(message.data.decode('UTF-8'))['task_id'])
