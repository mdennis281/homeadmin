from typing import List, Optional, Dict

# irrelevent 
BLACKLISTED_CHARACTERISTICS = [
    "CharacteristicValueActiveTransitionCount",
    "CharacteristicValueTransitionControl",
    "SupportedCharacteristicValueTransitionConfiguration"
]


class ServiceCharacteristic:
    def __init__(self, aid: int, iid: int, uuid: str, type: str, serviceType: str, serviceName: str, 
                 description: str, value, format: str, perms: List[str], canRead: bool, 
                 canWrite: bool, ev: bool, maxValue: Optional[int] = None, 
                 minValue: Optional[int] = None, minStep: Optional[int] = None, unit: Optional[str] = None):
        self.aid = aid
        self.iid = iid
        self.uuid = uuid
        self.type = type
        self.serviceType = serviceType
        self.serviceName = serviceName
        self.description = description
        self.value = value
        self.format = format
        self.perms = perms
        self.canRead = canRead
        self.canWrite = canWrite
        self.ev = ev
        self.maxValue = maxValue
        self.minValue = minValue
        self.minStep = minStep
        self.unit = unit

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            aid=data['aid'],
            iid=data['iid'],
            uuid=data['uuid'],
            type=data['type'],
            serviceType=data['serviceType'],
            serviceName=data['serviceName'],
            description=data['description'],
            value=data.get('value'),
            format=data['format'],
            perms=data['perms'],
            canRead=data['canRead'],
            canWrite=data['canWrite'],
            ev=data['ev'],
            maxValue=data.get('maxValue'),
            minValue=data.get('minValue'),
            minStep=data.get('minStep'),
            unit=data.get('unit')
        )

class AccessoryInformation:
    def __init__(self, Manufacturer: str, Model: str, Name: str, Serial_Number: str, Firmware_Revision: str, Configured_Name: str):
        self.Manufacturer = Manufacturer
        self.Model = Model
        self.Name = Name
        self.Serial_Number = Serial_Number
        self.Firmware_Revision = Firmware_Revision
        self.Configured_Name = Configured_Name

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            Manufacturer=data['Manufacturer'],
            Model=data['Model'],
            Name=data['Name'],
            Serial_Number=data['Serial Number'],
            Firmware_Revision=data['Firmware Revision'],
            Configured_Name=data.get('Configured Name')
        )

class Instance:
    def __init__(self, name: str, username: str, ipAddress: str, port: int, services: List, connectionFailedCount: int):
        self.name = name
        self.username = username
        self.ipAddress = ipAddress
        self.port = port
        self.services = services
        self.connectionFailedCount = connectionFailedCount

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data['name'],
            username=data['username'],
            ipAddress=data['ipAddress'],
            port=data['port'],
            services=data['services'],
            connectionFailedCount=data['connectionFailedCount']
        )

class Device:
    def __init__(self, aid: int, iid: int, uuid: str, type: str, humanType: str, serviceName: str, 
                 serviceCharacteristics: List[ServiceCharacteristic], accessoryInformation: AccessoryInformation, 
                 values: dict, instance: Instance, uniqueId: str):
        self.aid = aid
        self.iid = iid
        self.uuid = uuid
        self.type = type
        self.humanType = humanType
        self.serviceName = serviceName
        self.serviceCharacteristics = serviceCharacteristics
        self.accessoryInformation = accessoryInformation
        self.values = values
        self.instance = instance
        self.uniqueId = uniqueId
        self.changed_characteristics = []


    def get_characteristics(self) -> List[Dict]:
        """
        Returns a list of characteristics in the device.
        """
        return [{
            "type": char.type,
            "value": char.value,
            "description": char.description 
        } for char in self.serviceCharacteristics]

    def set_characteristic(self, characteristicType: str, value):
        """
        Sets the value of a characteristic if the input passes validation.
        
        :param characteristicType: The type of characteristic to set (string)
        :param value: The new value for the characteristic
        :raises ValueError: If validation fails
        """
        characteristic = next((c for c in self.serviceCharacteristics if c.type == characteristicType), None)
        
        if not characteristic:
            raise ValueError(f"Characteristic {characteristicType} not found.")

        # Check if the characteristic can be written to
        if not characteristic.canWrite:
            raise ValueError(f"Characteristic {characteristicType} cannot be written to.")

        # Check if the value is within min/max range (if applicable)
        if characteristic.minValue is not None and characteristic.maxValue is not None:
            if not (characteristic.minValue <= value <= characteristic.maxValue):
                raise ValueError(f"Value {value} for {characteristicType} is out of range. "
                                 f"Must be between {characteristic.minValue} and {characteristic.maxValue}.")

        # Check if the value is compatible with minStep (if applicable)
        if characteristic.minStep is not None:
            if (value - characteristic.minValue) % characteristic.minStep != 0:
                raise ValueError(f"Value {value} for {characteristicType} must be compatible with minStep "
                                 f"{characteristic.minStep}.")

        # Update the characteristic value if validation passes
        characteristic.value = value

        # Track changed characteristics
        self.changed_characteristics.append({
            "characteristicType": characteristic.type,
            "value": characteristic.value
        })

    def get_changed_characteristics(self) -> List[Dict]:
        """
        Returns a list of characteristics that have been changed.
        """
        return self.changed_characteristics
    
    def get_summary(self) -> dict:
        return {
                'uniqueId': self.uniqueId,
                'serviceName': self.serviceName,
                'type': self.type,
                'characteristics': [
                    {
                        'type': c.type,
                        'value': c.value,
                        'canRead': c.canRead,
                        'canWrite': c.canWrite,
                        'maxValue': c.maxValue,
                        'minValue': c.minValue,
                        'format': c.format
                    }
                    for c in self.serviceCharacteristics
                ]
            }
    
    def to_dict(self) -> dict:
        """
        Converts the Device object into a dictionary.
        """
        return {
            "aid": self.aid,
            "iid": self.iid,
            "uuid": self.uuid,
            "type": self.type,
            "humanType": self.humanType,
            "serviceName": self.serviceName,
            "serviceCharacteristics": [
                {
                    "aid": char.aid,
                    "iid": char.iid,
                    "uuid": char.uuid,
                    "type": char.type,
                    "serviceType": char.serviceType,
                    "serviceName": char.serviceName,
                    "description": char.description,
                    "value": char.value,
                    "format": char.format,
                    "perms": char.perms,
                    "maxValue": char.maxValue,
                    "minValue": char.minValue,
                    "minStep": char.minStep,
                    "canRead": char.canRead,
                    "canWrite": char.canWrite,
                    "ev": char.ev
                } for char in self.serviceCharacteristics
            ],
            "accessoryInformation": {
                "Manufacturer": self.accessoryInformation.Manufacturer,
                "Model": self.accessoryInformation.Model,
                "Name": self.accessoryInformation.Name,
                "Serial Number": self.accessoryInformation.Serial_Number,
                "Firmware Revision": self.accessoryInformation.Firmware_Revision,
                "Configured Name": self.accessoryInformation.Configured_Name
            },
            "values": self.values,
            "instance": {
                "name": self.instance.name,
                "username": self.instance.username,
                "ipAddress": self.instance.ipAddress,
                "port": self.instance.port,
                "services": self.instance.services,
                "connectionFailedCount": self.instance.connectionFailedCount
            },
            "uniqueId": self.uniqueId
        }

    @classmethod
    def from_dict(cls, data: Dict):
        # Create ServiceCharacteristics list
        service_characteristics = []
        for sc in data['serviceCharacteristics']:
            sc_obj = ServiceCharacteristic.from_dict(sc)
            if sc_obj.type not in BLACKLISTED_CHARACTERISTICS:
                service_characteristics.append(sc_obj)
        
        # Create AccessoryInformation and Instance objects
        accessory_info = AccessoryInformation.from_dict(data['accessoryInformation'])
        instance = Instance.from_dict(data['instance'])

        return cls(
            aid=data['aid'],
            iid=data['iid'],
            uuid=data['uuid'],
            type=data['type'],
            humanType=data['humanType'],
            serviceName=data['serviceName'],
            serviceCharacteristics=service_characteristics,
            accessoryInformation=accessory_info,
            values=data['values'],
            instance=instance,
            uniqueId=data['uniqueId']
        )
    

class ServiceIdentifier:
    def __init__(self, uniqueId: str, aid: int, iid: int, uuid: str):
        self.uniqueId = uniqueId
        self.aid = aid
        self.iid = iid
        self.uuid = uuid

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            uniqueId=data['uniqueId'],
            aid=data['aid'],
            iid=data['iid'],
            uuid=data['uuid']
        )

    def to_dict(self) -> dict:
        return {
            'uniqueId': self.uniqueId,
            'aid': self.aid,
            'iid': self.iid,
            'uuid': self.uuid
        }

class Room:
    def __init__(self, name: str, services: list):
        self.name = name
        self.services = [ServiceIdentifier.from_dict(service) for service in services]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            services=data['services']
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'services': [service.to_dict() for service in self.services]
        }

if __name__ == '__main__':

    # Example usage with your provided JSON data:
    import json

    json_data = '''[your json object here]'''
    devices_data = json.loads(json_data)

    # Create Device objects from the JSON list
    devices = [Device.from_dict(device_data) for device_data in devices_data]

    # Now `devices` contains instances of `Device` created from your JSON.
