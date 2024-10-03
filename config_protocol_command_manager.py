import time
import json
from logger import Logger
from hive_message import HiveMessage
from message_queue import MessageQueue
from app_settings import AppSettings
from config_message import ConfigMessage
from hive_node_manager import HiveNodeManager
from monitor_service import ServiceMonitor


class ConfigProtocolCommandManager:

    enable: bool = True

    def __init__(self, hive_node_manager: HiveNodeManager, outbound_message_queue: MessageQueue, service_monitor):
        
        self.logger: Logger = Logger()
        self.hive_node_manager: HiveNodeManager = hive_node_manager
        self.outbound_message_queue: MessageQueue = outbound_message_queue
        self.service_monitor: ServiceMonitor = service_monitor

        self.logger.debug("ConfigProtocolCommandManager", "ConfigProtocolCommandManager initialized...")

    def run(self) -> None:
        """
        Starts the config protocol by periodically sending config messages to random nodes in the network.
        """
        while True:
            if ConfigProtocolCommandManager.enable:
                self.logger.debug("ConfigProtocolCommandManager", "Running...")
                random_remote_node = self.hive_node_manager.get_random_live_node()
                
                if random_remote_node:
                    self.logger.info("ConfigProtocolCommandManager", f"Sending config to {random_remote_node.friendly_name}...")
                    config = json.dumps(self.service_monitor.config)
                    command_str = f"config {config}"
                    config_message = ConfigMessage(
                        sender=self.hive_node_manager.local_node,
                        recipient=random_remote_node,
                        command=command_str
                    )
                    new_hive_message = HiveMessage(config_message)
                    self.outbound_message_queue.enqueue(new_hive_message)

            time.sleep(AppSettings.HEARTBEAT_PROTOCOL_FREQUENCY_IN_SECONDS)

    def enable_config_protocol(self) -> None:
        """
        Enables the config protocol by setting the appropriate flag.
        """
        self.logger.debug("ConfigProtocolCommandManager", "Enabling config protocol...")
        ConfigProtocolCommandManager.enable = True

    def disable_config_protocol(self) -> None:
        """
        Disables the config protocol by setting the appropriate flag.
        """
        self.logger.debug("ConfigProtocolCommandManager", "Disabling config protocol...")
        ConfigProtocolCommandManager.enable = False
