import json
import psutil
import socket
from dataclasses import dataclass
from interface_utility import InterfaceContext
from states.listening import ListeningState
from constants import PORT


@dataclass
class IdleState:
    interface: InterfaceContext

    def setup(self, interface_name: str) -> None:
        interfaces = psutil.net_if_addrs()
        try:
            address = interfaces[interface_name][0].address
            self.interface.sock.bind((address, PORT))
            self.interface.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.interface.set_state(ListeningState(self.interface))
        except KeyError:
            print(f"Interface {interface_name} not found")
        except OSError as e:
            print(f"Error binding socket: {e}")
            self.interface.set_state(IdleState(self.interface))

    def setup_client(self, interface_name: str) -> None:
        self.setup(interface_name)

    def listening(self) -> None:
        pass
