from time import time

from base64 import b64encode
from hashlib import sha1
from secrets import randbelow

from mq.protocol.types import Message, MonitoringResult

"""
Expiration time set to 0 indicates that message never expires.
"""
never_expires : int = 0

id_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

id_length = 40


def create_message( m_pid:        str
                  , m_creator:    str
                  , m_expires_at: int
                  , m_spec:       str
                  , m_type:       str
                  , m_data:       bytes
                  , m_encrypted:  bool
                  , m_signature:  bytes) -> Message:
    msg = Message()
    m_id = get_id()
    m_created_at = epoch_time()

    msg.id = m_id
    msg.pid = m_pid
    msg.creator = m_creator
    msg.created_at = m_created_at
    msg.expires_at = m_expires_at
    msg.spec = m_spec
    msg.type = m_type
    msg.data = m_data
    msg.encrypted = m_encrypted
    msg.signature = m_signature

    return msg


def create_mon_result( r_name:    str
                     , r_host:    str
                     , r_running: bool
                     , r_message: str) -> MonitoringResult:
    mon_result = MonitoringResult()

    mon_result.sync_time  = epoch_time()
    mon_result.name       = r_name
    mon_result.host       = r_host
    mon_result.is_running = r_running
    mon_result.message    = r_message

    return mon_result


def mon_result_to_json(mon_result):
    alive = str(mon_result.is_running is not None and mon_result.is_running).lower()
    mon_message = ('{ \"sync_time\" : %s, \"name\" : \"%s\", \"is_alive\" : %s, \"message\" : \"%s\"}' % (
        mon_result.sync_time
        , mon_result.name
        , alive
        , mon_result.message)).encode('UTF-8')
    return mon_message


def get_id() -> bytes:
    return "".join([id_alphabet[randbelow(len(id_alphabet))] for i in range(0, id_length)])

def epoch_time() -> int:
    return int(time() * 1000)
