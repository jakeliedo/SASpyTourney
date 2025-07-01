from saspy.sas import Sas
from state import state
import time
import threading
from saspy.models.EftStatement import EftStatement

# Lock toàn cục để tránh xung đột truy cập cổng COM
serial_lock = threading.Lock()

# Khởi tạo kết nối với máy slot qua giao thức SAS

def setup_sas():
    sas = Sas(port='COM4', baudrate=19200, timeout=1, perpetual=True)
    addr = None
    connected = False
    while not connected:
        try:
            print("⏳ Thử handshake với máy slot trên COM4")
            with serial_lock:
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

def event_poll_safe(sas):
    try:
        with serial_lock:
            return sas.events_poll()  # Trả về đúng raw string
    except Exception as e:
        return 'ERR'


def poll_loop(sas):
    while True:
        state['event'] = event_poll_safe(sas)
        print(f"[Poll] event = {state['event']}")
        time.sleep(1)


def credit_loop(sas):
    while True:
        try:
            with serial_lock:
                c = sas.current_credits()
            state['credit'] = c
            state['last_updated'] = time.strftime("%H:%M:%S")
        except Exception as e:
            state['credit'] = 'ERR'
            print(f"[Credit] ❌ Exception: {e!r}")
        print(f"[Credit] {state['credit']} @ {state['last_updated']}")
        time.sleep(2)

def meters_loop(sas):
    while True:
        try:
            with serial_lock:
                meters = sas.meters(denom=True)
            state['meters'] = meters
        except Exception as e:
            state['meters'] = 'ERR'
            print(f"[Meters] ❌ Exception: {e!r}")
        print(f"[Meters] {state['meters']}")
        time.sleep(5)

def game_features_loop(sas):
    while True:
        try:
            with serial_lock:
                features = sas.enabled_features(game_number=0)
            state['features'] = features
        except Exception as e:
            state['features'] = 'ERR'
            print(f"[Features] ❌ Exception: {e!r}")
        print(f"[Features] {state['features']}")
        time.sleep(10)

def eft_status_loop(sas):
    while True:
        try:
            # Tạm thời tạo dữ liệu mẫu từ EftStatement (vì chưa có logic đọc thực tế từ sas)
            status = EftStatement(
                eft_status="Connected",
                promo_amount="0.00",
                cashable_amount="0.00",
                eft_transfer_counter="0"
            )
            state['eft_status'] = status.__dict__
        except Exception as e:
            state['eft_status'] = 'ERR'
            print(f"[EFT] ❌ Exception: {e!r}")
        print(f"[EFT] {state['eft_status']}")
        time.sleep(15)

def start_all_threads(sas):
    threading.Thread(target=poll_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=credit_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=meters_loop, args=(sas,), daemon=True).start()
    threading.Thread(target=game_features_loop, args=(sas,), daemon=True).start()
    #threading.Thread(target=eft_status_loop, args=(sas,), daemon=True).start()
    print("✅ Tất cả các thread trạng thái đã khởi động")
