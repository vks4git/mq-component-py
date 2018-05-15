from mq.component import Component
from mq.protocol import message_type, message_spec, create_message, never_expires
from json import loads


class Calculator(Component):
    """
    Simple component example.
    It receives a config message with JSON-encoded data which contains two operands and action and sends back the result.
    write_log function is used here as an example.
    """

    def run(self, sched_out, contr_out, sched_in, message):
        while True:
            tag, msg = sched_out.recv_multipart()
            if message_type(tag) == 'config' and message_spec(tag) == 'example_calculator':
                self.write_log('received message from %s' % msg.id.decode('UTF-8'))
                msg_data = loads(msg.data.decode('UTF-8'))
                op1 = msg_data['first']
                op2 = msg_data['second']
                act = msg_data['action']
                res = None
                if act == '+':
                    res = op1 + op2
                elif act == '*':
                    res = op1 * op2
                if res is None:
                    self.write_log('Unknown action %s received from %s' % (act, msg.id.decode('UTF-8')), log_type = 'warning')
                    answer = create_message(msg.id, self.get_config().creator, never_expires, 'example_calculator', 'JSON', 'error', b'{ "error": "unknown action %s" }' % res.encode('UTF-8'))
                else:
                    self.write_log('Result sent back to %s' % msg.id.decode('UTF-8'))
                    answer = create_message(msg.id, self.get_config().creator, never_expires, 'example_calculator', 'JSON', 'result', b'{ "answer": %s }' % str(res).encode('UTF-8'))
                sched_in.send(answer)


if __name__ == "__main__":
    comp = Calculator("example_calculator-py")
