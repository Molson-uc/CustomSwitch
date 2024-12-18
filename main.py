import socket
import threading
import psutil
from queue import Queue
from collections import defaultdict
from states.idle import IdleState
from interface_utility import InterfaceState
from constants import BUFFER, INTERNAL_IF, EXTERNAL_IF, IP_EG1, PORT

client_queue = defaultdict(Queue)


class Interface:
    def __init__(self, input_queue: Queue, output_queue: Queue):
        self.state: InterfaceState = IdleState(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.input_queue = input_queue
        self.output_queue = output_queue

    def set_state(self, state: InterfaceState) -> None:
        self.state = state

    def setup(self, interface_name: str) -> None:
        self.state.setup(interface_name)

    def listening(self) -> None:
        self.state.listening()

    def accept(self) -> None:
        self.state.accept()


def setup_interface(
    interface_name: str, input_queue: Queue, output_queue: Queue
) -> None:
    interface = Interface(input_queue, output_queue)
    try:
        interface.setup(interface_name)
        interface.listening()
        while True:
            interface.accept()
    except Exception as e:
        print(f"Error setting up interface: {e}")


if __name__ == "__main__":
    i_queue = Queue()
    o_queue = Queue()

    threading.Thread(
        target=setup_interface, args=(INTERNAL_IF, i_queue, o_queue)
    ).start()
    threading.Thread(
        target=setup_interface, args=(EXTERNAL_IF, o_queue, i_queue)
    ).start()

    with open("policy.json") as file:
        msg_pack = file.read()

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.connect((IP_EG1, PORT))
        while True:
            if not i_queue.empty():
                msg = i_queue.get()
                soc.send(msg.encode())
                res = soc.recv(BUFFER).decode()
                if res:
                    o_queue.put(res)
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        soc.close()
