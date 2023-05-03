import json

from junior.flaskProject.application.models import Action
from junior.flaskProject.application.services.snmp_executor import SNMPExecutor
from junior.flaskProject.application.services.device import Device

device = Device.to_model(**{"ip": "192.168.31.149"})
action = Action.to_model(**{"cmd": "ifOutOctets"})

with SNMPExecutor("public", device) as snmp:
    last = snmp.execute(action)
    resp = snmp.execute(action, last)
print(json.dumps(resp, indent=2))
