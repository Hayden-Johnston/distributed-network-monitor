# author: Hayden Johnston
# date: 04/24/2024
# description: echo server with TCP socket implementation utilizing provided course examples


import datetime
import json
import os
from logger import Logger
from hive_node_manager import HiveNodeManager
from network_monitoring_examples import check_server_http, check_dns_server_status, check_ntp_server, check_tcp_port, check_server_https, check_udp_port

def get_timestamp():
    ''' Helper function to return current timestamp'''
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return timestamp

class ServiceMonitor():

    def __init__(self, local_name, config, lock):
        self.logger: Logger = Logger()
        self.config = config
        self.local_name = local_name
        self.lock = lock


    def monitor_loop(self):
        ''' Infinite loop to echo status of tracked services'''
        while(1):
            config_file_name = f"{self.local_name}.json"
            if os.path.exists(config_file_name):
                try:
                    with self.lock.acquire(timeout=1):
                        with open(config_file_name, 'r') as file:
                            check_config = json.load(file)
                            if self.config[self.local_name] != check_config[self.local_name]:
                                self.config[self.local_name] = check_config[self.local_name]
                except:
                    pass
            for key in self.config[self.local_name][1]:
                # get time of last check and frequency 
                timestamp = datetime.datetime.strptime(self.config[self.local_name][1][key][0], "%Y-%m-%d %H:%M:%S")
                frequency = datetime.timedelta(seconds=int(self.config[self.local_name][1][key][2]))
                
                if datetime.datetime.strptime(get_timestamp(), "%Y-%m-%d %H:%M:%S") >= timestamp + frequency:
                    service_type = self.config[self.local_name][1][key][1]

                    # print monitoring data for each server/service
                    self.config[self.local_name][1][key][0] = get_timestamp()
                    if service_type == 'HTTP':
                        service_response = check_server_http(self.config[self.local_name][1][key][3])
                    elif service_type == 'HTTPS':
                        service_response = check_server_https(self.config[self.local_name][1][key][3])
                    elif service_type == 'NTP':
                        service_response = check_ntp_server(self.config[self.local_name][1][key][3])
                    elif service_type == 'DNS':
                        service_response = check_dns_server_status(self.config[self.local_name][1][key][3], self.config[self.local_name][1][key][4], self.config[self.local_name][1][key][5])
                    elif service_type == 'UDP':
                        service_response = check_udp_port(self.config[self.local_name][1][key][3], int(self.config[self.local_name][1][key][4]))
                    elif service_type == 'TCP':
                        service_response = check_tcp_port(self.config[self.local_name][1][key][3], int(self.config[self.local_name][1][key][4]))

                    if service_response[0] == True:
                        status = "GOOD"
                    else:
                        status = "ERROR"

                    output = f"{status} - {key} - {service_type} - {service_response}"
                    self.logger.info("ServiceMonitor", output)
                    if os.path.exists(config_file_name):
                        os.remove(config_file_name)
                    with open(config_file_name, 'w') as file:
                        json.dump(self.config, file, indent=4)
