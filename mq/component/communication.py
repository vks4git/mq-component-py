import msgpack
import zmq

from mq.protocol import Message, message_tag, MQError, error_transport


class IncomingDecorator:
    """
    Incoming ZMQ socket decorator.
    Provides method recv_multipart() called the same in ZMQ socket.
    Unpacks received message and tag and also updates current task id.
    Current task id will be used while handling kill messages.
    """

    def __init__(self, error_send, logger, channel_in, task_id):
        self._channel_in = channel_in
        self._task_id = task_id
        self.logger = logger

    def recv_multipart(self):
        success = False
        while not success:
            try:
                packed_tag, packed_message = self._channel_in.recv_multipart()
                tag = msgpack.unpackb(packed_tag)
                message = Message()
                message.unpack(packed_message)
            except Exception as e:
                error_msg = 'Communicational incoming decorator :: %s' % format(e)
                self.logger.write_log(error_msg, log_type = 'error')
                self.error_send.send(MQError(error_transport, error_msg))
            else:
                success = True
        return (tag, message)


class OutgoingDecorator:
    """
    Outgoing ZMQ socket decorator.
    Provides a convenient way to send a message: user must just create it, 
    the message will be packed and sent via send_multipart with its tag automatically.
    """

    def __init__(self, channel_out):
        self._channel_out = channel_out

    def send(self, message):
        tag = message_tag(message)
        packed_message = message.pack()
        packed_tag = msgpack.packb(tag, use_bin_type=True)
        self._channel_out.send_multipart([packed_tag, packed_message])

    def send_multipart(self, tag, message):
        self._channel_out.send_multipart([tag, packed_message])


def default_communication(error_send, logger, config, action, shared_message, task_id, master_send):
    """
    Communication level dispatcher. It provides user incoming communication channels from the scheduler and
    controller and an outgoing channel to controller. It also provides a shared string variable which user is free
    to modify. Its value will be included into monitoring message, so common use for it is to describe what's going
    on at the moment.
    """
    context = zmq.Context()

    from_scheduler = context.socket(zmq.SUB)
    from_scheduler.setsockopt(zmq.SUBSCRIBE, b'')
    from_scheduler.connect("tcp://" + config.scheduler_out['host'] + ':' + str(config.scheduler_out['comport']))

    to_scheduler = context.socket(zmq.PUSH)
    to_scheduler.connect("tcp://" + config.scheduler_in['host'] + ':' + str(config.scheduler_in['comport']))

    from_controller = None
    if config.controller_port is not None:
        from_controller = context.socket(zmq.PULL)
        from_controller.connect("tcp://" + config.controller_host + ':' + str(config.controller_port))

    from_sched_decorated = IncomingDecorator(error_send, logger, from_scheduler, task_id)
    from_contr_decorated = IncomingDecorator(error_send, logger, from_controller, task_id)
    to_sched_decorated = OutgoingDecorator(to_scheduler)

    action(from_sched_decorated, from_contr_decorated, to_sched_decorated, shared_message, master_send)
