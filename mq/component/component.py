import multiprocessing as mp
import zmq
from ctypes import c_char_p

from mq.component.communication import default_communication
from mq.component.monitoring import default_monitor
from mq.component.technical import default_tech_listener
from mq.config import Config


class Component:
    """
    A MoniQue component.
    It behaves as described below:
    * On creation three processes are spawned: technical listener, communication process and monitoring sender.
    * User implements communication logic via implementation of @run@ method in Component class descendants.
    * Technical listener communicates with the master-process using pipe without duplex. 
    * When a kill message is received, communication process restarts.

    Component uses three shared between processes variables:
    * shared_message: user-defined variable which is included in monitoring message.
    * is_alive: set to True iff communicational process works properly. Included in monitoring message.
    * task_id: current task id. Compared with kill_task_id from kill message.

    """

    def __init__(self, name):
        self._config = Config(name)

        manager = mp.Manager()

        self.shared_message = manager.Value(c_char_p, '')
        self.is_alive = manager.Value(bool, False)
        self.task_id = manager.Value(c_char_p, '')

        self._tech_master, self._tech_child = mp.Pipe(duplex=True)

        self._tech_listen = mp.Process(target=default_tech_listener,
                                       args=(self._config, self._tech_child,),
                                       name='Technical channel listener')

        self._monitor = mp.Process(target=default_monitor,
                                   args=(self._config, self.shared_message, self.is_alive,),
                                   name='Monitoring sender')

        self._communication = mp.Process(target=default_communication,
                                         args=(self._config, self.run, self.shared_message, self.task_id,),
                                         name='Communication channel – scheduler')

        self._tech_listen.start()
        self._communication.start()
        self.is_alive.value = True
        self._monitor.start()

        while True:
            kill_id = self._tech_master.recv()
            if self.task_id == kill_id and self._communication is not None:
                self._communication.terminate()
                self.is_alive.value = False
                self._communication = mp.Process(target=default_communication,
                                                 args=(self._config, self.run, self.shared_message, self.task_id,),
                                                 name='Communication channel – scheduler')
                self._communication.start()
                self.is_alive.value = True

    def run(self, sched_out, contr_out, sched_in, message):
        pass

    def get_config(self):
        return self._config

    def terminate(self):
        self._communication.terminate()
        self._tech_listen.terminate()
        self._monitor.terminate()
