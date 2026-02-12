
import socket
import os
import git
from datetime import datetime

# Try to import bluetooth, skip if not available
try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False

# Try to import signals (hardware), skip if not available
try:
    from signals import listen_electric_signals, listen_led_signals
    SIGNALS_AVAILABLE = True
except ImportError:
    SIGNALS_AVAILABLE = False

GIT_REPO_PATH = os.path.abspath('.')
GIT_COMMIT_MSG = 'Auto update commands'
DATA_FILE = 'commands_log.txt'

def save_command(source, command):
    with open(DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] {source}: {command}\n")
    try:
        push_to_github()
    except Exception as e:
        print(f"[GitHub] Upload error: {e}")

def listen_wifi_commands(port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    print(f"[WiFi] Waiting for commands on port {port}...")
    conn, addr = s.accept()
    with conn:
        print(f"[WiFi] Connection from {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode('utf-8')
            print(f"[WiFi] Command: {command}")
            save_command('WiFi', command)

def listen_bluetooth_commands(port=3):
    if not BLUETOOTH_AVAILABLE:
        print("[Bluetooth] Module not available. Skipping Bluetooth commands.")
        return
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)
    print(f"[Bluetooth] Waiting for commands on port {port}...")
    client_sock, address = server_sock.accept()
    print(f"[Bluetooth] Connection from {address}")
    while True:
        data = client_sock.recv(1024)
        if not data:
            break
        command = data.decode('utf-8')
        print(f"[Bluetooth] Command: {command}")
        save_command('Bluetooth', command)

def push_to_github():
    repo = git.Repo(GIT_REPO_PATH)
    repo.git.add(DATA_FILE)
    repo.index.commit(GIT_COMMIT_MSG)
    origin = repo.remote(name='origin')
    origin.push()
    print('[GitHub] Data pushed successfully.')

if __name__ == '__main__':
    try:
        listen_wifi_commands()
    except Exception as e:
        print(f"[WiFi] Error: {e}")
    try:
        listen_bluetooth_commands()
    except Exception as e:
        print(f"[Bluetooth] Error: {e}")
    if SIGNALS_AVAILABLE:
        try:
            for signal in listen_electric_signals(10):
                save_command('Electric', signal)
        except Exception as e:
            print(f"[Electric] Error: {e}")
        try:
            for led in listen_led_signals(10):
                save_command('LED', led)
        except Exception as e:
            print(f"[LED] Error: {e}")
    else:
        print("[Signals] Hardware signal modules not available. Skipping electric/LED signals.")
