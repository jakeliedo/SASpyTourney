import os, sys

# chèn thư mục libs vào front của sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
SYS_LIBS = os.path.join(ROOT, 'libs')
SASPY_DIR = os.path.join(SYS_LIBS, 'saspy')
sys.path.insert(0, SYS_LIBS)
sys.path.insert(0, SASPY_DIR)

print(">> sys.path =", sys.path)
 
from saspy.sas import Sas
from tournament import TournamentManager
from state import state
import threading, time
from api_server import app

def setup_sas():
    sas = Sas(port='COM5', baudrate=19200, timeout=1, perpetual=True)
    # Loop retry handshake cho đến khi thành công
    while True:
        try:
            print("⏳ Thử handshake với slot máy trên COM5…")
            addr = sas.start()   # vừa open port, vừa handshake
            print(f"✅ Handshake OK, slot address = {hex(addr)}")
            state['address'] = hex(addr)
            break
        except Exception as e:
            print(f"❌ Handshake thất bại: {e!r}, retry sau 3s")
            time.sleep(3)
    return sas

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

def run_flask():
    print("🌐 Flask server đang khởi động tại http://localhost:5000 ...")
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Lỗi khi chạy Flask: {e!r}")

if __name__ == '__main__':
    print("▶️  Main process started")
    
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask thread khởi động tại http://localhost:5000")
    try:
        sas = setup_sas()
        print("🔧 Bắt đầu setup SAS")
    
        tm = TournamentManager()
        print("✅ TournamentManager khởi tạo")
    
    # Ví dụ bắt đầu session – bạn có thể comment hoặc điều chỉnh
        tm.start('player001', state['address'], state['credit'])
        print("▶️  Tournament session started for player001")

    # Khởi thread polling + thread đọc credit
        threading.Thread(target=poll_loop, args=(sas,), daemon=True).start()
        threading.Thread(target=credit_loop, args=(sas,), daemon=True).start()

    except Exception as e:
        print(f"⚠️ Không kết nối được máy slot: {e!r}")  

    # Khởi Flask API trong thread riêng và bật debug
    #threading.Thread(
        #target=lambda: app.run(
            #host='0.0.0.0', 
            #port=5000, 
            #debug=True,
            #use_reloader=False
    # ),
        #daemon=True
    #).start()
    #print("✅ Host started. Visit http://localhost:5000")
    #def run_flask():
    #    print("[FLASK] 🔄 Flask thread bắt đầu...")
    #    try:
    #        app.run(
    #            host='0.0.0.0',
    #            port=5000,
    #            debug=True,
    #            use_reloader=False
    #    )
    #    except Exception as e:
    #       print(f"[FLASK] ❌ Flask lỗi: {e!r}")

    # Main thread in state luân phiên
    try:
        while True:
            # In ra state 10s/lần để kiểm tra
            print("----- Current State -----")
            print(state)
            print("-------------------------")
            time.sleep(10)
    except KeyboardInterrupt:
        print("🛑 Program stopped by user")