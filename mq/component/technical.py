import zmq
import msgpack
from mq.protocol import message_type, message_spec, Message, MQError, error_technical
import json


def default_tech_listener(error_send, logger, config, master_send):
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
        try:
            packed_tag, packed_message = channel.recv_multipart()
            tag = msgpack.unpackb(packed_tag)
            message = Message()
            message.unpack(packed_message)

            msg_type = message_type(tag)
            msg_spec = message_spec(tag)
            if msg_type == 'config' and msg_spec == 'kill':
                master_send.send(json.loads(message.data.decode('UTF-8'))['task_id'])
        except Exception as e:
            error_msg = 'Technical listener :: %s' % format(e)
            logger.write_log(error_msg, log_type='error')
            error_send.send(MQError(error_technical, error_msg))
