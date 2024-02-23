import csv
import requests
import time
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def check_ip_port(ip, port):
    url = f"http://{ip}:{port}"  # Assuming HTTP
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }
    try:
        response = requests.get(url, timeout=2, allow_redirects=True, verify=False, headers=headers)
        if response.status_code == 500:
            log_error(ip, port)
    except requests.exceptions.Timeout:
        pass  # Ignore timed-out connections
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.SSLError):
            print(f"SSL error connecting to {ip}:{port}: {e}")
        else:
            print(f"Error connecting to {ip}:{port}: {e}")

def log_error(ip, port):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("error_log.csv", "a") as logfile:
        writer = csv.writer(logfile)
        writer.writerow([timestamp, ip, port])

def main():
    # Read IPs and ports from CSV file
    with open("cwsc_all.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)
        ip_port_list = list(reader)

    # Function to process each IP-port pair
    def process_ip_port(ip_port):
        ip, port = ip_port
        try:
            ip_address = ipaddress.ip_address(ip)
            if isinstance(ip_address, ipaddress.IPv6Address):
                return
        except ValueError:
            pass
        check_ip_port(ip, port)

    # Create a ThreadPoolExecutor with a maximum of 2 threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_ip_port, ip_port_list)

if __name__ == "__main__":
    main()
