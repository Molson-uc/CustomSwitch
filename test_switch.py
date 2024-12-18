import pytest
from unittest.mock import MagicMock, patch
from queue import Queue
from main import Interface
from states.idle import IdleState
from states.connected import ConnectedState
from constants import BUFFER, EXTERNAL_IF

ADDRESS = "192.168.0.1"
POLICY = '{"dst_phys": "test"}'
PORT = 5050


@pytest.fixture
def setup_interface():
    input_queue = Queue()
    output_queue = Queue()
    interface = Interface(input_queue, output_queue)
    return interface, input_queue, output_queue


def test_set_state(setup_interface):
    interface, _, _ = setup_interface
    new_state = IdleState(interface)
    interface.set_state(new_state)
    assert interface.state == new_state


def test_setup_idle_state(setup_interface):
    interface, _, _ = setup_interface
    with patch(
        "main.psutil.net_if_addrs",
        return_value={EXTERNAL_IF: [MagicMock(address=ADDRESS)]},
    ):
        idle_state = IdleState(interface)
        idle_state.setup(EXTERNAL_IF)
        assert (
            interface.state.__class__.__name__ == "ListeningState"
            or interface.state.__class__.__name__ == "IdleState"
        )


def test_accept_connected_state(setup_interface):
    interface, _, _ = setup_interface
    mock_client = MagicMock()
    mock_client.recv.return_value = b"test_data"
    with patch(
        "main.socket.socket.accept", return_value=(mock_client, (ADDRESS, PORT))
    ):
        connected_state = ConnectedState(interface)
        interface.set_state(connected_state)
        client = interface.state.accept()
        assert client is not None


def test_connected_read_queue(setup_interface):
    interface, input_queue, _ = setup_interface
    connected_state = ConnectedState(interface)
    interface.set_state(connected_state)
    input_queue.put("test_data")
    result = connected_state.read_queue(input_queue, ADDRESS)
    assert result == "test_data"


def test_connected_get_policy(setup_interface):
    interface, _, _ = setup_interface
    connected_state = ConnectedState(interface)
    policy = connected_state._ConnectedState__get_policy(POLICY)
    assert policy == {"dst_phys": "test"}


def test_connected_get_policy_invalid_json(setup_interface):
    interface, _, _ = setup_interface
    connected_state = ConnectedState(interface)
    policy = connected_state._ConnectedState__get_policy("invalid json")
    assert policy == {}


def test_connected_get_dst_phys(setup_interface):
    interface, _, _ = setup_interface
    connected_state = ConnectedState(interface)
    dst = connected_state._ConnectedState__get_dst_phys({"dst_phys": "test"})
    assert dst == "test"


def test_connected_get_dst_phys_none(setup_interface):
    interface, _, _ = setup_interface
    connected_state = ConnectedState(interface)
    dst = connected_state._ConnectedState__get_dst_phys(None)
    assert dst == "NONE"
