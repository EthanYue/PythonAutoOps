import logging
from device import DeviceDBHandler
from action import ActionJSONHandler
from executor import SSHExecutor

SSH_USERNAME = "cisco"
SSH_PASSWORD = "cisco"
SSH_SECRET = "cisco"
device_filter = {"ip": "192.168.31.149"}
action_filter = {"name": "version_check"}


if __name__ == '__main__':
    logging.basicConfig(filename="ssh_executor.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    try:
        device_handler = DeviceDBHandler("root", "Yfy98333498", "localhost", "python_ops")
        action_handler = ActionJSONHandler("action.json")
        executor = SSHExecutor(
            username=SSH_USERNAME, password=SSH_PASSWORD, secret=SSH_SECRET, device_condition=device_filter,
            device_handler=device_handler, action_handler=action_handler, logger=logger)
        print(executor.device_type)
        print(executor.conn.base_prompt)
        # print(executor.fetch_action(action_filter))
        output = executor.execute(action_condition=action_filter)
        print(output)
        executor.close()
    except Exception as e:
        logger.error(str(e))
