from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Device(object):
    name: str
    vid: int
    pid: int


class HCIInterface(ABC):
    '''
    HCI interface
    '''
    @property
    def name(self):
        return ''

    @abstractmethod
    def list_devices(self):
        '''
        list devices
        '''
        return None

    @abstractmethod
    def open(self, device: Device=None):
        '''
        open hci
        '''
        pass

    @abstractmethod
    def close(self):
        '''
        close hci
        '''
        pass

    @abstractmethod
    def send_command(self, cmd: bytes):
        '''
        send command
        '''
        pass

    @abstractmethod
    def register_event(self, cb: callable):
        '''
        register event callback
        '''
        pass

    @abstractmethod
    def receive_event(self) -> bytes:
        pass
