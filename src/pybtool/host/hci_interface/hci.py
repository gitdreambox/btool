from abc import ABC, abstractmethod

class HCIInterface(ABC):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send_command(self, command):
        pass

    @abstractmethod
    def receive_event(self):
        pass