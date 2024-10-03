import argparse
import threading
import os
import json
from filelock import FileLock, Timeout
from typing import Optional
from logger import Logger
from hive_node import HiveNode
from message_queue import MessageQueue
from hive_node_manager import HiveNodeManager
from hive_receiver_service import HiveReceiverService
from hive_sender_client import HiveSenderClient
from monitor_service import ServiceMonitor
from cli_command_processor import CliCommandProcessor
from inbound_queue_command_processor import InboundQueueCommandProcessor
from gossip_protocol_command_manager import GossipProtocolCommandManager
from heartbeat_protocol_command_manager import HeartbeatProtocolCommandManager
from config_protocol_command_manager import ConfigProtocolCommandManager
from app_settings import AppSettings


class AppMain:
    """
    AppMain is the main entry point for the Hive network application.

    Attributes:
    ----------
    logger : Logger
        An instance of the Logger class for logging messages.
    cli_command_processor : Optional[CliCommandProcessor]
        An instance of the CliCommandProcessor for processing CLI commands.
    outbound_message_queue : MessageQueue
        A queue for outbound messages.
    inbound_message_queue : MessageQueue
        A queue for inbound messages.
    hive_node_manager : Optional[HiveNodeManager]
        Manages the nodes in the Hive network.
    """

    def __init__(self):
        """
        Initializes a new instance of AppMain.
        """
        self.logger: Logger = Logger()
        self.cli_command_processor: Optional[CliCommandProcessor] = None
        self.outbound_message_queue: MessageQueue = MessageQueue("Outbound")
        self.inbound_message_queue: MessageQueue = MessageQueue("Inbound")
        self.hive_node_manager: Optional[HiveNodeManager] = None
        self.configuration = {}

    def run(self) -> None:
        """
        Starts the Hive network application by parsing arguments, setting up the local node,
        and initializing various components such as the Hive service, client, and command processors.
        """
        parser = argparse.ArgumentParser(description='Start a TCP server.')
        parser.add_argument('-ip', type=str, default=AppSettings.DEFAULT_IP_ADDRESS, help='IP address to bind the server')
        parser.add_argument('-port', type=int, default=AppSettings.DEFAULT_PORT_NUMBER, help='Port to bind the server')
        parser.add_argument('-friendly_name', type=str, default=AppSettings.DEFAULT_FRIENDLY_NAME, help='Friendly name for the local node')
        args = parser.parse_args()

        # Set the log file name based on the friendly_name
        log_file_name = f"app.{args.friendly_name.replace(' ', '_')}.log"
        self.logger.set_log_file(log_file_name)

        self.logger.debug("AppMain", f"Arguments: {args}")

        local_node: HiveNode = HiveNode(args.friendly_name, args.ip, args.port, is_local_node=True)
        self.configuration[args.friendly_name] = []
        # Hive Node Manager
        self.hive_node_manager = HiveNodeManager(local_node)

        # Set the config file name based on the friendly_name
        config_file_name = f"{args.friendly_name.replace(' ', '_')}.json"
        lock_path = f"{config_file_name}.lock"
        lock = FileLock(lock_path)
        if os.path.exists(config_file_name):
            with open(config_file_name, 'r') as file:
                self.configuration = json.load(file)

        # Service Monitor Thread
        service_monitor = ServiceMonitor(args.friendly_name, self.configuration, lock)
        service_monitor_thread = threading.Thread(target=service_monitor.monitor_loop, daemon=True)
        service_monitor_thread.start()

        # Hive service server thread
        hive_service = HiveReceiverService(local_node.friendly_name, local_node.ip_address, local_node.port_number, self.hive_node_manager, self.inbound_message_queue, self.outbound_message_queue, service_monitor, lock)
        hive_service_thread = threading.Thread(target=hive_service.run, daemon=True)
        hive_service_thread.start()

        # Hive client thread
        hive_client = HiveSenderClient(self.outbound_message_queue, self.inbound_message_queue)
        hive_client_thread = threading.Thread(target=hive_client.run, daemon=True)
        hive_client_thread.start()

        # Queue Command Processor
        inbound_queue_command_processor = InboundQueueCommandProcessor(self.hive_node_manager, self.outbound_message_queue, self.inbound_message_queue)
        inbound_queue_command_processor_thread = threading.Thread(target=inbound_queue_command_processor.run, daemon=True)
        inbound_queue_command_processor_thread.start()

        # Gossip Protocol Command Manager
        gossip_protocol_command_manager = GossipProtocolCommandManager(self.hive_node_manager, self.outbound_message_queue)
        gossip_protocol_command_manager_thread = threading.Thread(target=gossip_protocol_command_manager.run, daemon=True)
        gossip_protocol_command_manager_thread.start()

        # Heartbeat Protocol Command Manager
        heartbeat_protocol_command_manager = HeartbeatProtocolCommandManager(self.hive_node_manager, self.outbound_message_queue)
        heartbeat_protocol_command_manager_thread = threading.Thread(target=heartbeat_protocol_command_manager.run, daemon=True)
        heartbeat_protocol_command_manager_thread.start()

        # Config Protocol Command Manager
        config_protocol_command_manager = ConfigProtocolCommandManager(self.hive_node_manager, self.outbound_message_queue, service_monitor)
        config_protocol_command_manager_thread = threading.Thread(target=config_protocol_command_manager.run, daemon=True)
        config_protocol_command_manager_thread.start()

        # CLI Command Processor
        self.cli_command_processor = CliCommandProcessor(self.hive_node_manager, self.outbound_message_queue, self.inbound_message_queue)
        self.cli_command_processor.set_prompt(f"{local_node.friendly_name}> ")
        self.cli_command_processor.command_loop()


if __name__ == "__main__":
    app = AppMain()
    app.run()
