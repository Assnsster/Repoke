import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# Biến để giữ số lượng kết nối thành công
good_count = 0
lock = threading.Lock()

def is_vnc_port(address):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(address)
        sock.sendall(b'\x03')  # Gửi byte 0x03 (version 3.003)
        response = sock.recv(12)

        if response.startswith(b"RFB"):
            return True
    except Exception as e:
        print(f"Failed to check VNC on {address[0]}:{address[1]}: {e}")
    finally:
        sock.close()

    return False

def connect_vnc(address, password):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(address)

        sock.sendall(password.encode())
        response = sock.recv(1024)
        print(f"Connected to {address[0]}:{address[1]} - Response: {response.decode()}")
        return True
    except Exception as e:
        print(f"Failed to connect to {address[0]}:{address[1]}: {e}")
    finally:
        sock.close()

    return False

def process_line_type1(line, output_file, error_file):
    global good_count
    try:
        parts = line.strip().split('-')
        if len(parts) == 3:
            address_port = parts[0].split(':')
            address = address_port[0]
            port = int(address_port[1])
            password = parts[1]
            domain = parts[2].strip('[]')

            if is_vnc_port((address, port)):
                print(f"{address}:{port} is a VNC server.")
                if connect_vnc((address, port), password):
                    with lock:
                        good_count += 1
                        with open(output_file, 'a') as gcf:
                            gcf.write(f"{address}:{port}\\{domain}\\{password}\n")
            else:
                print(f"{address}:{port} is not a VNC server.")
    except Exception as e:
        print(f"Error processing line: {e}")
        with open(error_file, 'a') as ef:
            ef.write(f"Failed to process line {line}: {e}\n")

def process_line_type2(line, output_file, error_file):
    global good_count
    try:
        parts = line.strip().split('\\')
        if len(parts) >= 3:
            address_port = parts[0].split(':')
            address = address_port[0]
            port = int(address_port[1])
            domain = parts[1]
            password = parts[-1]

            if is_vnc_port((address, port)):
                print(f"{address}:{port} is a VNC server.")
                if connect_vnc((address, port), password):
                    with lock:
                        good_count += 1
                        with open(output_file, 'a') as gcf:
                            gcf.write(f"{address}:{port}\\{domain}\\{password}\n")
            else:
                print(f"{address}:{port} is not a VNC server.")
    except Exception as e:
        print(f"Error processing line: {e}")
        with open(error_file, 'a') as ef:
            ef.write(f"Failed to process line {line}: {e}\n")

def scan_vnc_concurrently(input_file, output_file, error_file, max_threads=50, scan_type=2):
    global good_count
    try:
        with open(input_file, 'r', encoding='ISO-8859-1') as infile:
            lines = infile.readlines()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            if scan_type == 1:
                futures = [executor.submit(process_line_type1, line, output_file, error_file) for line in lines]
            else:
                futures = [executor.submit(process_line_type2, line, output_file, error_file) for line in lines]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred during execution: {e}")

    except Exception as e:
        print(f"An error occurred while scanning: {e}")

def display_good_count():
    while True:
        input("Nhấn Enter để hiển thị số lượng kết nối thành công...")
        with lock:
            print(f"Số lượng kết nối thành công: {good_count}")

def main():
    # Sử dụng argparse để xử lý các tùy chọn từ dòng lệnh
    parser = argparse.ArgumentParser(description="VNC Scanner")
    parser.add_argument("-i", "--input", help="Input file with IP addresses", required=True)
    parser.add_argument("-o", "--output", help="Output file to store successful connections", required=True)
    parser.add_argument("-e", "--error", help="Error file to log failed connections", default="errors.txt")
    parser.add_argument("-t", "--threads", help="Number of threads to use for scanning", type=int, default=50)
    parser.add_argument("-T", "--type", help="Type of input format (1 or 2)", type=int, choices=[1, 2], default=2)

    args = parser.parse_args()

    # Tạo và bắt đầu thread để hiển thị số lượng kết nối
    display_thread = threading.Thread(target=display_good_count)
    display_thread.start()

    # Thực hiện quét với các tùy chọn do người dùng cung cấp
    scan_vnc_concurrently(args.input, args.output, args.error, max_threads=args.threads, scan_type=args.type)

if __name__ == "__main__":
    main()

