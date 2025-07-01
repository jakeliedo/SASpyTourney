from saspy.sas import Sas
from state import state
import time
import threading

# Khởi tạo kết nối với máy slot qua giao thức SAS

def setup_sas():
    sas = Sas(port='COM4', baudrate=19200, timeout=1, perpetual=True)
    addr = None
    connected = False
    while not connected:
        try:
            print(f"⏳ Thử handshake với máy slot trên {sas.port}")
            addr = sas.start()

            if isinstance(addr, str) and addr.isdigit():
                addr = int(addr)

            if isinstance(addr, int):
                print(f"✅ Handshake OK, slot address = {hex(addr)}")
                state['address'] = hex(addr)
                connected = True
            else:
                print(f"❌ Handshake thất bại: Không nhận địa chỉ hợp lệ, addr={addr!r}")
                time.sleep(3)

        except Exception as e:
            print(f"❌ Handshake thất bại: addr={addr!r}, lỗi: {e}, retry sau 3s")
            time.sleep(3)

    return sas

# Các vòng lặp trạng thái chính

def poll_loop(sas):
    while True:
        try:
            ev = sas.events_poll()
            state['event'] = hex(ev)
        except Exception as e:
            state['event'] = 'ERR'
        print(f"[Poll] event = {state['event']}")
        time.sleep(1)

def credit_loop(sas):
    while True:
        try:
            c = sas.current_credits()
            state['credit'] = c
            state['last_updated'] = time.strftime("%H:%M:%S")
        except Exception as e:
            state['credit'] = -1
        print(f"[Credit] {state['credit']} @ {state['last_updated']}")
        time.sleep(2)

def meters_loop(sas):
    while True:
        try:
            meters = sas.read_meters()
            state['meters'] = meters
        except Exception as e:
            state['meters'] = 'ERR'
        print(f"[Meters] {state['meters']}")
        time.sleep(5)

def game_features_loop(sas):
    while True:
        try:
            features = sas.game_features()
            state['features'] = features
        except Exception as e:
            state['features'] = 'ERR'
        print(f"[Features] {state['features']}")
        time.sleep(10)

def eft_status_loop(sas):
    while True:
        try:
            status = sas.eft_status()
            state['eft_status'] = status
        except Exception as e:
            state['eft_status'] = 'ERR'
        print(f"[EFT] {state['eft_status']}")
        time.sleep(15)

def start_all_threads(sas):
    threading.Thread(target=poll_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=credit_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=meters_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=game_features_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=eft_status_loop, args=(sas,), daemon=True).start()
    print("✅ Tất cả các thread trạng thái đã khởi động")
