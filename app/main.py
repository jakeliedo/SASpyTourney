import os, sys
import threading, time
from tournament import TournamentManager
from state import state
from api_server import app

# Chèn thư mục libs vào sys.path nếu chưa có
ROOT = os.path.dirname(os.path.dirname(__file__))
SYS_LIBS = os.path.join(ROOT, 'libs')
SASPY_DIR = os.path.join(SYS_LIBS, 'saspy')
sys.path.insert(0, SYS_LIBS)
sys.path.insert(0, SASPY_DIR)

print(">> sys.path =", sys.path)

from saspy.sas import Sas
from sas_module import setup_sas, start_all_threads

def run_flask():
    print("🌐 Tạo Flask server http://localhost:5000")
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

    # Khởi động Flask server trong thread nền
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask thread đã khởi động tại http://localhost:5000")

    try:
        sas = setup_sas()
        print("🎰 Bắt đầu setup SAS")

        tm = TournamentManager()
        print("🏁 TournamentManager khởi tạo")

        tm.start('player001', state['address'], state['credit'])
        print("✅ Tournament session started for player001")

        start_all_threads(sas)

    except Exception as e:
        print(f"🚫 Không kết nối được máy slot: {e!r}")

    # In trạng thái mỗi 10 giây
    try:
        while True:
            print("----- Current State -----")
            print(state)
            print("-------------------------")
            time.sleep(10)
    except KeyboardInterrupt:
        print("🛑 Program stopped by user")
