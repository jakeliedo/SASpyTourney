import serial
import serial.tools.list_ports
import time

def find_slot_machine_port(
    test_string=b'Ready\r\n',  # Chuỗi nhận dạng từ máy slot
    baudrate=9600,
    timeout=1
):
    """Tự động tìm cổng COM kết nối với máy slot"""
    print("🔍 Đang tìm kiếm cổng kết nối máy slot...")
    
    # Lấy danh sách tất cả cổng COM
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        print(f"   Kiểm tra {port.device}...")
        try:
            # Thử kết nối từng cổng
            with serial.Serial(port.device, baudrate=baudrate, timeout=timeout) as ser:
                # Đợi máy slot khởi động
                time.sleep(2)
                
                # Xóa buffer
                ser.reset_input_buffer()
                
                # Đọc dữ liệu từ cổng COM
                data = ser.readline()
                
                # Kiểm tra chuỗi nhận dạng
                if test_string in data:
                    print(f"✅ Tìm thấy máy slot tại {port.device}")
                    return port.device
                
        except (OSError, serial.SerialException):
            continue
            
    print("❌ Không tìm thấy máy slot trên bất kỳ cổng COM nào")
    return None