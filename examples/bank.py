from mq.component import Component
from mq.protocol import message_type, message_spec, message_pid, create_message, never_expires
from json import dumps, loads


class Bank(Component):
    """
    Simple component example.
    It receives a config message with JSON-encoded data which contains monthly income and period length in month.
    Using calculator_py component it calculates total income and sends it back.
    Monitoring message variable is updated here as an example.
    """

    def run(self, sched_out, contr_out, sched_in, message):
        while True:
            tag, msg = sched_out.recv_multipart()
            if message_type(tag) == 'config' and message_spec(tag) == 'example_bank':
                message.value = 'received message from %s' % msg.id.decode('UTF-8')
                msg_data = loads(msg.data.decode('UTF-8'))
                months = msg_data['months']
                per_month = msg_data['per_month']

                calculator_json = dumps({'first' : float(months), 'second' : float(per_month), 'action' : '*'}).encode('UTF-8')
                calculator_msg = create_message(msg.id, self.get_config().creator, never_expires, 'example_calculator', 'JSON', 'config', calculator_json)
                sched_in.send(calculator_msg)
                while True:
                    response_tag, response = sched_out.recv_multipart()
                    if message_type(response_tag) == 'result' and message_spec(response_tag) == 'example_calculator' and message_pid(response_tag) == calculator_msg.id:
                        calculator_result = loads(response.data.decode('UTF-8'))
                        res = calculator_result['answer']
                        message.value = 'Result sent back to %s' % msg.id.decode('UTF-8')
                        answer = create_message(msg.id, self.get_config().creator, never_expires, 'example_bank', 'JSON', 'result', b'{ "total": %s }' % str(res).encode('UTF-8'))
                        sched_in.send(answer)
                        break

if __name__ == "__main__":
    comp = Bank("example_bank-py")
