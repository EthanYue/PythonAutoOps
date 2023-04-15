import json
from io import StringIO
from typing import List, Dict

from textfsm import TextFSM
from netmiko import ConnectHandler
from os import environ

environ["NTC_TEMPLATES_DIR"] = "/"


def parse_from_str(output: str, template: str) -> List[Dict]:
    fsm = TextFSM(StringIO(template))
    res = fsm.ParseTextToDicts(output)
    return res


def connect(params: Dict, command: str, template: str):
    conn = ConnectHandler(**params)
    output = conn.send_command(command)
    res = parse_from_str(output, template)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    params = {
        "device_type": "cisco_ios",
        "host": "192.168.31.149",
        "username": "cisco",
        "password": "cisco"
    }
    template = """Value VERSION (.+?)
Value ROMMON (\S+)
Value HOSTNAME (\S+)
Value UPTIME (.+)
Value UPTIME_YEARS (\d+)
Value UPTIME_WEEKS (\d+)
Value UPTIME_DAYS (\d+)
Value UPTIME_HOURS (\d+)
Value UPTIME_MINUTES (\d+)
Value RELOAD_REASON (.+?)
Value RUNNING_IMAGE (\S+)
Value List HARDWARE (\S+|\S+\d\S+)
Value List SERIAL (\S+)
Value CONFIG_REGISTER (\S+)
Value List MAC ([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})
Value RESTARTED (.+)

Start
  ^.*Software\s.+\),\sVersion\s${VERSION},*\s+RELEASE.*
  ^ROM:\s+${ROMMON}
  ^\s*${HOSTNAME}\s+uptime\s+is\s+${UPTIME} -> Continue
  ^.*\s+uptime\s+is.*\s+${UPTIME_YEARS}\syear -> Continue
  ^.*\s+uptime\s+is.*\s+${UPTIME_WEEKS}\sweek -> Continue
  ^.*\s+uptime\s+is.*\s+${UPTIME_DAYS}\sday -> Continue
  ^.*\s+uptime\s+is.*\s+${UPTIME_HOURS}\shour -> Continue
  ^.*\s+uptime\s+is.*\s+${UPTIME_MINUTES}\sminute
  ^[sS]ystem\s+image\s+file\s+is\s+"(.*?):${RUNNING_IMAGE}"
  ^(?:[lL]ast\s+reload\s+reason:|System\s+returned\s+to\s+ROM\s+by)\s+${RELOAD_REASON}\s*$$
  ^[Pp]rocessor\s+board\s+ID\s+${SERIAL}
  ^[Cc]isco\s+${HARDWARE}\s+\(.+\).+
  ^[Cc]onfiguration\s+register\s+is\s+${CONFIG_REGISTER}
  ^Base\s+[Ee]thernet\s+MAC\s+[Aa]ddress\s+:\s+${MAC}
  ^System\s+restarted\s+at\s+${RESTARTED}$$
  ^Switch\s+Port -> Stack
  # Capture time-stamp if vty line has command time-stamping turned on
  ^Switch\s\d+ -> Stack
  ^Load\s+for\s+
  ^Time\s+source\s+is


Stack
  ^[Ss]ystem\s+[Ss]erial\s+[Nn]umber\s+:\s+${SERIAL}
  ^[Mm]odel\s+[Nn]umber\s+:\s+${HARDWARE}\s*
  ^[Cc]onfiguration\s+register\s+is\s+${CONFIG_REGISTER}
  ^Base [Ee]thernet MAC [Aa]ddress\s+:\s+${MAC}
"""
    command = "show version"
    connect(params, command, template)