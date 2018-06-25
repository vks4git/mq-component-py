import zmq
import msgpack
from mq.protocol import create_mon_result, create_message, mon_result_to_json, never_expires, message_tag, MQError, error_technical
import time


def default_monitor(error_send, logger, config, shared_message, is_alive):
    """
    Monitoring process body.
    Sends a monitoring message to scheduler every @frequency@ (from config.json) milliseconds.
    """
    context = zmq.Context()
    channel = context.socket(zmq.PUSH)
    channel.connect("tcp://" + config.scheduler_in['host'] + ':' + str(config.scheduler_in['techport']))

    delay = config.mon_frequency / 1000

    while True:
        try:
            message = shared_message.value
            status = is_alive.value

            time.sleep(delay)
            res = create_mon_result(config.name, "", status, message)
            msg = create_message('', config.creator, never_expires, 'monitoring', 'data', res.pack(), False, b'')
            tag = message_tag(msg)
            channel.send_multipart([msgpack.packb(tag, use_bin_type=True), msg.pack()])
        except Exception as e:
            error_msg = 'Monitoring :: %s' % format(e)
            logger.write_log(error_msg, log_type = 'error')
            error_send.send(MQError(error_technical, error_msg))
