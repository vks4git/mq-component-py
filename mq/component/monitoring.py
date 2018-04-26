import zmq
import msgpack
from mq.protocol.functions import create_mon_result, create_message, mon_result_to_json
from mq.protocol.tag import message_tag
import time


def default_monitor(config, shared_message, is_alive):
    """
    Monitoring process body.
    Sends a monitoring message to scheduler every @frequency@ (from config.json) milliseconds.
    """
    context = zmq.Context()
    channel = context.socket(zmq.PUSH)
    channel.connect("tcp://" + config.scheduler_in['host'] + ':' + str(config.scheduler_in['techport']))

    delay = config.mon_frequency / 1000

    while True:
        message = shared_message.value
        status = is_alive.value

        time.sleep(delay)
        res = create_mon_result(config.name, "", status, message)
        msg = create_message(b'', config.creator, 1e17, 'monitor', 'JSON', 'config', mon_result_to_json(res))
        tag = message_tag(msg)
        channel.send_multipart([msgpack.packb(tag, use_bin_type=True), msg.pack()])
