from sconfig import *
import socket, threading, subprocess

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def media_control(sock, addr): 
    print('media_control')
    mcmd = sock.recv(2).decode(FORMAT)
    print(f'$ {mcmd}')
    if mcmd in m_commands:
        if callable(m_commands[mcmd]):
            m_commands[mcmd]()
        else:
            subprocess.run(m_commands[mcmd])

def adjust_position(delta_seconds):
    current_pos = float(subprocess.check_output(['playerctl', 'position']).decode().strip())
    new_pos = current_pos + delta_seconds
    subprocess.run(['playerctl', 'position', str(new_pos)])

m_commands = {
    'tr' : ['playerctl', 'position', '0'],
    'vu' : ['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%+'],
    'vm' : ['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
    'pt' : ['playerctl', 'previous'],
    'pp' : ['playerctl', 'play-pause'],
    'nt' : ['playerctl', 'next'],
    'rt' : lambda: adjust_position(-10),
    'vd' : ['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%-'],
    'st' : lambda: adjust_position(10),
}

def command_control(sock, addr): 
    print('command_control')
    ccmd = sock.recv(1).decode(FORMAT)
    chash = sock.recv(32).decode(FORMAT)
    if ccmd in c_commands:
        print(f'$ {ccmd}')
        if chash == c_commands[ccmd][1]:
            print(f'$ {chash}')
            cmd, expected_hash = c_commands[ccmd]

            if chash == expected_hash:
                if callable(cmd):
                    cmd()
                else:
                    subprocess.run(cmd)


def mng_hctl():pass

c_commands = {
    'l' : (['loginctl', 'lock-session'], 'a664814c0cf72d9f02625bf2e75fc607'),
    'd' : (mng_hctl, 'cb9804ac3b4740c9e72366918a5dd749'),
    's' : (['shutdown'], '1f6cf66fea5c83bb41387d3e0f82c986'),
    'c' : (['shutdown', '-c'], '1f11c1afb9c65669691219c34dd01a06'),
    'r' : (['reboot'], '0cdc38fb30c99db9345daf36e940ec21'),
    'b' : (['safeeyes', '-t'], 'efa27a9d6a7b720a074acebb31976b57')
}

functions = {
    "m" : media_control,
    "c" : command_control
}

def handler(sock, addr):
    ctype = sock.recv(1).decode(FORMAT)
    print(ctype)
    if ctype:
        print(f'>> {ctype}')
        if ctype in functions:
            functions[ctype](sock, addr)
    sock.close() 
    

def home():
    try:
        tcp_server.bind(("0.0.0.0", SERVER_PORT))
        tcp_server.listen()
        while True:
            try:
                sock, addr = tcp_server.accept()
                print('new')
                thread = threading.Thread(target=handler, args=(sock, addr))
                thread.start()
            except Exception as e: print(f'>> error: {e}')
                
    except Exception as e: print(f'>> error: {e}')
    finally: tcp_server.close()
    

if __name__ == "__main__":
    try:
        home()
    except Exception as e: print(f'>> error: {e}')