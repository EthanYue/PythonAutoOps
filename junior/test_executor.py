import logging
from device import DeviceDBHandler
from action import ActionJSONHandler, Action
from executor import SSHExecutor

SSH_USERNAME = "cisco"
SSH_PASSWORD = "cisco"

device_filter = {"ip": "192.168.31.149"}
action_filter = {"name": "power_check"}


if __name__ == '__main__':
    logging.basicConfig(filename="ssh_executor.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    try:
        device_handler = DeviceDBHandler("root", "Yfy98333498", "localhost", "python_ops")
        action_handler = ActionJSONHandler("action.json")
        executor = SSHExecutor(username=SSH_USERNAME, password=SSH_PASSWORD, device_condition=device_filter,
                               device_handler=device_handler, action_handler=action_handler, logger=logger)
        output = executor.execute(action=Action.to_model(cmd="show ip interface brief"))
        logger.info(output)
        executor.close()
    except Exception as e:
        logger.error(str(e))

