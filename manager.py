# author: Hayden Johnston
# date: 04/24/2024
# description: Network monitoring script - builds list of servers/services to monitor - logs status in terminal
#              Utilizes a suite of provided example functions for checking status of services.
# TODO: error handling for add/remove functions

from network_monitoring_examples import check_server_http, check_dns_server_status, check_ntp_server, check_tcp_port, check_server_https, check_udp_port
import keyboard, datetime, time, json, os, socket, threading
from socket_client import config_socket

datafile = 'services.json'
# load data if file exists
if os.path.exists(datafile):
    with open(datafile, 'r') as file:
        tracked_services = json.load(file)
else:
    # initialize empty dict for hosts & services
    services = {}  # {host_name: [(ip, port), {service_name: [data]}]}

threads = []

def monitor_loop(services):
    ''' Legacy code - either fix for new config or remove
    Infinite loop to echo status of tracked_services'''
    print("")
    print("Network Monitoring - 'q' to exit\n")
    # break flag used to exit infinite while loop from the internal for loop
    break_flag = 1
    while(break_flag == 1):
        for key in services:

            # allow user to exit loop with hotkey 'q'
            if keyboard.is_pressed('q'):
                break_flag = 0

            # get time of last check and frequency 
            timestamp = datetime.datetime.strptime(services[key][0], "%Y-%m-%d %H:%M:%S")
            frequency = datetime.timedelta(seconds=int(services[key][2]))
            
            if datetime.datetime.strptime(get_timestamp(), "%Y-%m-%d %H:%M:%S") >= timestamp + frequency:
                service_type = services[key][1]

                # print monitoring data for each server/service
                services[key][0] = get_timestamp()
                if key == "echo server":
                    service_response = check_echo_server()
                elif service_type == 'HTTP':
                    service_response = check_server_http(services[key][3])
                elif service_type == 'HTTPS':
                    service_response = check_server_https(services[key][3])
                elif service_type == 'NTP':
                    service_response = check_ntp_server(services[key][3])
                elif service_type == 'DNS':
                    service_response = check_dns_server_status(services[key][3], services[key][4], services[key][5])
                elif service_type == 'UDP':
                    service_response = check_udp_port(services[key][3], int(services[key][4]))
                elif service_type == 'TCP':
                    service_response = check_tcp_port(services[key][3], int(services[key][4]))

                if service_response[0] == True:
                    status = "GOOD"
                else:
                    status = "ERROR"

                print(f"{services[key][0]} - {status} - {key} - {service_type} - {service_response}") # return this string to manager

                # write/overwrite json datafile if it exists
                if os.path.exists(datafile):
                    os.remove(datafile)
                with open(datafile, 'w') as file:
                    json.dump(tracked_services, file)
    
    # return to dashboard when loop breaks
    show_dashboard()

def start_monitor():
    for host in tracked_services:
        ip = tracked_services[host][0][0]
        port = int(tracked_services[host][0][1])
        config = json.dumps(tracked_services[host][1])
        socket = config_socket(ip, port)
        thread = threading.Thread(target=run_thread, args=(config, socket, host))
        threads.append(thread)
        thread.start()

def run_thread(config, socket, host):
    ''' Send config to host and begin listening for service'''
    # Send data
    # print(f"Config sent: {config}")
    socket.sendall(config.encode())

    while not keyboard.is_pressed('q'):
        # Receive data
        response = socket.recv(1024)
        # if not response:
        #     socket.close()
        #     new_socket = None
        #     for i in range(5):
        #         if new_socket == None:
        #             print(f"Attempt {i + 1} - reconnection to {host}")
        #             check_port = check_tcp_port(tracked_services[host][0][0], int(tracked_services[host][0][1]))
        #             if check_port[0]:
        #                 new_socket = config_socket(tracked_services[host][0][0], int(tracked_services[host][0][1]))
        #                 run_thread(config, new_socket, host)
        #             time.sleep(5)
        #     time.sleep(300)
        if response != "":
            print(f"{host} - {response.decode()}")

    socket.close()

    show_dashboard()

def add_host():
    ''' Allows user to add host for distributed monitoring service'''
    print("")
    print("Add host\n")
    host_name = input("enter name for host: \n")
    print("")
    host_ip = input("enter IP for TCP socket: \n")
    print("")
    host_port = int(input("enter port for TCP socket: \n"))

    tracked_services[host_name] = [(host_ip, host_port), {}]

    write_data()

    show_dashboard()

def list_hosts():
    print("\nHosts available:\n")
    for key in tracked_services:
        print(f"{key} - {tracked_services[key][0][0]}:{tracked_services[key][0][1]}")

    show_dashboard()

def remove_host():
    ''' Prompts user to choose a host to remove from the tracking list'''
    print("")
    delete_host = input("Input name of host to remove:\n")
    try:
        removed_host = tracked_services.pop(delete_host)
    except:
        print("Host not found")
    finally:
        if removed_host is not None:
            print("")
            print("Successfully removed ", delete_host, " ", removed_host)
    
    write_data()
    
    show_dashboard()

def add_service():
    ''' Allows user to add service to monitor
    # Structure of an added service:
    # {name: [timestamp, type, frequency, server/URL/IP, PORT/query, record_type]}
    #
    # Data for each service type
    # HTTP/HTTPS: URL
    # NTP: server
    # DNS: server, query, record_type
    # UDP/TCP: IP, PORT
    '''

    print("")
    print("Add server/service")
    service_host = None
    while service_host not in tracked_services:
        service_host = input("Input name of host: \n")
        if service_host not in tracked_services:
            print("host not found - reenter host name")
    print("select type of service")
    print(" '1' - HTTP")
    print(" '2' - HTTPS")
    print(" '3' - NTP")
    print(" '4' - DNS")
    print(" '5' - UDP")
    print(" '6' - TCP")

    choices = ('1', '2', '3', '4', '5', '6')
    key = 0
    while key not in choices:
        key = input()
        if key not in choices:
            print(choices)
            print("Invalid input, choose an option from the dashboard")
    
    if key == '1':
        # add HTTP entry
        service_type = 'HTTP'
    if key == '2':
        # add HTTPS entry
        service_type = 'HTTPS'
    if key == '3':
        # add NTP entry
        service_type = 'NTP'
    if key == '4':
        # add DNS entry
        service_type = 'DNS'
    if key == '5':
        # add UDP entry
        service_type = 'UDP'
    if key == '6':
        # add TCP entry
        service_type = 'TCP'
    
    print("")
    service_name = input("Input name of this service\n")

    print("")
    service_frequency = input("Input monitoring frequency (seconds)\n")

    print("")
    print("Input one:")
    print("URL for HTTP/HTTPS")
    print("server for DNS/NTP")
    print("IP for UDP/TCP")
    service_domain = input()

    print("")
    service_direct = None
    if service_type in ('DNS', 'UDP', 'TCP'):
        print("Input one:")
        print("query for DNS")
        print("PORT for UDP/TCP")
        service_direct = input()
    
    record_type = None
    if service_type in ('DNS'):
        print("")
        record_type = input("Input record type for DNS (A, CNAME)\n")

    tracked_services[service_host][1][service_name] = ([get_timestamp(), service_type, service_frequency, service_domain, service_direct, record_type])

    write_data()

    show_dashboard()

def list_services():
    ''' Print a list of all tracked servers/services'''
    for host in tracked_services:
        print(f"\nHost: {host}")
        for key, value in tracked_services[host][1].items():
            print(key, " - ", value)

    show_dashboard()
    
def remove_service():
    ''' Prompts user to choose a service to remove from the tracking list'''
    print("")
    service_host = None
    while service_host not in tracked_services:
        service_host = input("Input name of host:\n")
        if service_host not in tracked_services:
            print("host not found - reenter host name\n")
    delete_service = input("Input name of service to stop tracking\n")
    try:
        removed_service = tracked_services[service_host][1].pop(delete_service)
    except:
        print("Service not found")
    finally:
        if removed_service is not None:
            print("")
            print("Successfully removed ", delete_service, " ", removed_service)
    
    write_data()
    
    show_dashboard()

def get_timestamp():
    ''' Helper function to return current timestamp'''
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return timestamp

def write_data():
    ''' Helper function to write current service data to file'''
    # write/overwrite json datafile if it exists
    if os.path.exists(datafile):
        os.remove(datafile)
    with open(datafile, 'w') as file:
        json.dump(tracked_services, file, indent=4)

def check_echo_server():
    ''' Check echo server status on local machine'''
    # Create a socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Specify server IP and port
    server_addr = '127.0.0.1'
    server_port  = 5150

    response = None
    try:
        # Try to connect
        client_sock.connect((server_addr, server_port))

        # Send data
        message = "1"
        client_sock.sendall(message.encode())

        # Receive data
        response = client_sock.recv(1024)
    
    except:
        return (False, "Echo server not responding")
        
    finally:
        # Close the connection
        client_sock.close()

        if response != None and response.decode() == "1":
            return (True, "Echo server is listening for connections")
        else:
            return (False, "Echo server not responding")

def show_dashboard():
    ''' Show dashboard where users can choose what page to view'''
    print("")
    print("Network Monitor Dashboard")
    print("-----------------------------")
    print(" 't' - Start")
    print(" 'q' - Exit")
    print("-----------------------------")
    print(" 'h' - Add host")
    print(" 'k' - List hosts")
    print(" 'e' - Remove host")
    print("-----------------------------")
    print(" 'a' - Add server/service")
    print(" 'l' - List servers/services")
    print(" 'r' - Remove server/service")

    # for thread in threads:
    #     try:
    #         thread.join()
    #         threads.remove(thread)
    #     except:
    #         pass
    
    # define valid user input
    choices = ('t', 'a', 'l', 'r', 'q', 'h', 'k', 'e')
    key = 0
    while key not in choices:
        key = input()
        if key not in choices:
            print("Invalid input, choose an option from the dashboard")

    # define actions for user input
    if key == 't':
        start_monitor()
        pass
    if key == 'h':
        add_host()
    if key == 'k':
        list_hosts()
    if key == 'e':
        remove_host()
    if key == 'a':
        add_service()
    if key == 'l':
        list_services()
    if key == 'r':
        remove_service()
    if key == 'q':
        exit()


if __name__ == '__main__':
    show_dashboard()