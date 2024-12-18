from dataclasses import dataclass
from interface_utility import InterfaceContext
from states.connected import ConnectedState


@dataclass
class ListeningState:
    interface: InterfaceContext

    def setup(self) -> None:
        print(f"Interface is set up. You are in ListeningState")

    def listening(self) -> None:
        self.interface.sock.listen(5)
        self.interface.set_state(ConnectedState(self.interface))
