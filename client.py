from flask import Flask, render_template, request
import socket

TARGET_IP = "192.168.29.51" 
TARGET_PORT = 6900
FORMAT = 'utf-8'
TARGET_ADDRESS = (TARGET_IP, TARGET_PORT)

c_commands = {
    'l' : 'a664814c0cf72d9f02625bf2e75fc607',
    'd' : 'cb9804ac3b4740c9e72366918a5dd749',
    's' : '1f6cf66fea5c83bb41387d3e0f82c986',
    'c' : '1f11c1afb9c65669691219c34dd01a06',
    'r' : '0cdc38fb30c99db9345daf36e940ec21',
    'b' : 'efa27a9d6a7b720a074acebb31976b57'
}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html") 

@app.route("/m", methods=["POST"])
def receive_media_cmd():
    data = request.json
    print("Received:", data["value"])
    send_media_cmd(data["value"])
    return "OK"

@app.route("/c", methods=["POST"])
def receive_command_cmd():
    data = request.json
    print("Received:", data["value"])
    send_command_cmd(data["value"])
    return "OK"

def send_media_cmd(n):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(TARGET_ADDRESS)
        s.sendall(b"m")
        s.sendall(n.encode(FORMAT))

def send_command_cmd(n):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  
        s.connect(TARGET_ADDRESS)
        if n in c_commands:
            s.sendall(b"c")
            s.sendall(n.encode(FORMAT))
            s.sendall(c_commands[n].encode(FORMAT))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)