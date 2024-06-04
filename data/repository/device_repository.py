import json
import sqlite3 as sql

import paho.mqtt.client as mqtt_client

from data.model.device import Device, Config, Potentiometer, PotentiometerConfig


class DeviceRepository:
    def __init__(self, filename: str):
        self._conn = sql.connect(filename, check_same_thread=False)
        broker = "broker.emqx.io"
        self._client = mqtt_client.Client()
        self._client.connect(broker)
        self._client.loop_start()

    async def update_mqtt_device(self, device_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "SELECT mac_address, active_config FROM devices WHERE id = ?",
            (str(device_id)),
        )
        query = cur.fetchone()
        print(query)
        mac = query[0]
        config_id = query[1]
        if config_id is None:
            return
        config_id = int(config_id)
        configs = await self.get_potentiometer_configs(config_id)
        result = []
        for config in configs:
            p = await self.get_potentiometer(config.potentiometer_id)
            result.append({
                'id': config.id,
                'value': config.value,
                'potentiometer_id': config.potentiometer_id,
                'config_id': config.config_id,
                'name': p.name,
            })
        result = json.dumps(result)
        self._client.publish(f"isu/potentiometers/{mac}/update", str(result))
        print(f"Published {str(result)} to isu/potentiometers/{mac}/update")

    async def create_device(self, name: str, mac_address: str, user_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO devices (name, mac_address, user_id) VALUES (?, ?, ?)",
            (name, mac_address, user_id),
        )
        self._conn.commit()

    async def get_devices(self, user_id: int) -> list[Device]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM devices WHERE user_id = ?",
            (str(user_id)),
        )
        fetched_devices = cur.fetchall()
        devices = []
        for device in fetched_devices:
            config_id = None
            if device[2] is not None:
                config_id = int(device[2])
            devices.append(
                Device(id=int(device[0]), name=device[1], active_config=config_id, mac_address=device[3],
                       user_id=int(device[4]))
            )
        return devices

    async def set_active_config(self, device_id: int, config_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE devices SET active_config = ? WHERE id = ?",
            (str(config_id), str(device_id)),
        )
        self._conn.commit()
        await self.update_mqtt_device(device_id)

    async def get_active_config(self, device_id: int) -> Config | None:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM devices WHERE id = ?",
            (str(device_id)),
        )
        config_id = cur.fetchone()[2]
        if config_id is None:
            return None
        config_id = int(config_id)
        return await self.get_config(config_id)

    async def create_config(self, name: str, device_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO configs (name, device_id) VALUES (?, ?)",
            (name, str(device_id))
        )
        self._conn.commit()

    async def get_configs(self, device_id: int) -> list[Config]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM configs WHERE device_id = ?",
            (str(device_id))
        )
        fetched_configs = cur.fetchall()
        configs = []
        for config in fetched_configs:
            configs.append(
                Config(id=int(config[0]), name=config[1], device_id=int(config[2]))
            )
        return configs

    async def get_config(self, config_id: int) -> Config:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM configs WHERE id = ?",
            (str(config_id))
        )
        config = cur.fetchone()
        return Config(id=int(config[0]), name=config[1], device_id=int(config[2]))

    async def create_potentiometer(self, name: str, device_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO potentiometers (name, device_id) VALUES (?, ?)",
            (name, str(device_id))
        )
        self._conn.commit()

    async def get_potentiometers(self, device_id: int) -> list[Potentiometer]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM potentiometers WHERE device_id = ?",
            (str(device_id))
        )
        fetched_potentiometers = cur.fetchall()
        potentiometers = []
        for p in fetched_potentiometers:
            potentiometers.append(
                Potentiometer(id=int(p[0]), name=p[1], device_id=int(p[2]))
            )
        return potentiometers

    async def get_potentiometer(self, potentiometer_id: int) -> Potentiometer:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM potentiometers WHERE id = ?",
            (str(potentiometer_id))
        )
        p = cur.fetchone()
        return Potentiometer(id=int(p[0]), name=p[1], device_id=int(p[2]))

    async def create_potentiometer_config(self, device_id: int, value: int, potentiometer_id: int, config_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO potentiometer_configs (value, potentiometer_id, config_id) VALUES (?, ?, ?)",
            (value, str(potentiometer_id), str(config_id))
        )
        self._conn.commit()
        await self.update_mqtt_device(device_id)

    async def get_potentiometer_configs(self, config_id: int) -> list[PotentiometerConfig]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM potentiometer_configs WHERE config_id = ?",
            (str(config_id))
        )
        fetched_potentiometers = cur.fetchall()
        potentiometers = []
        for p in fetched_potentiometers:
            potentiometers.append(
                PotentiometerConfig(id=int(p[0]), value=p[1], potentiometer_id=int(p[2]), config_id=int(p[3]))
            )
        return potentiometers

    async def update_potentiometer_config(self, device_id: int, potentiometer_config_id: int, value: int):
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE potentiometer_configs SET value = ? WHERE id = ?",
            (value, str(potentiometer_config_id)),
        )
        self._conn.commit()
        await self.update_mqtt_device(device_id)

    def close(self):
        self._conn.close()
        self._client.disconnect()
        self._client.loop_stop()
