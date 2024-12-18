import json
import socket
import threading
from queue import Queue
from dataclasses import dataclass
from interface_utility import InterfaceContext
from constants import BUFFER


@dataclass
class ConnectedState:
    interface: InterfaceContext

    def accept(self) -> None:
        try:
            client, client_addr = self.interface.sock.accept()
            client.setblocking(False)
            threading.Thread(
                target=self.connected, args=(client, client_addr[0])
            ).start()
            return client
        except socket.error as e:
            print(f"Error accepting connection: {e}")
            return None

    def read_queue(self, queue: Queue, ip: str):
        return queue.get() if not queue.empty() else None

    def connected(self, client: socket.socket, ip: str) -> None:
        sequence = 0
        while client:
            try:
                client_data = client.recv(BUFFER).decode()
                if client_data:
                    sequence += 1
                    if client_data == "end":
                        break

                    policy = self.__get_policy(client_data)
                    dst = self.__get_dst_phys(policy)

                    if dst:
                        self.interface.output_queue.put(client_data)

                    data_from_socket = self.read_queue(self.interface.input_queue, ip)
                    if data_from_socket:
                        client.send(data_from_socket.encode())
                        sequence += 1

                    if sequence == 2:
                        break
            except Exception as e:
                print(f"Error during communication: {e}")
        try:
            client.close()
        except Exception as e:
            print(f"Error closing client connection: {e}")

    def __get_policy(self, data: str) -> dict:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
            return {}

    def __get_dst_phys(self, policy: dict) -> str:
        if policy is None:
            return "NONE"
        return policy.get("dst_phys", "NONE")
