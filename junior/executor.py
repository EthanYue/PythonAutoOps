from netmiko import ConnectHandler

params = {
    "device_type": "cisco_ios", 
    "host": "192.168.31.149", 
    "username": "cisco", 
    "password": "cisco"
}
net_connect = ConnectHandler(**params)
cmd = "show interface brief"
output = net_connect.send_command(cmd, expect_string=net_connect.base_prompt, read_timeout=60 * 5)
net_connect.send_config_set("", exit_config_mode=False)
print(output)
