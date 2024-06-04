import sqlite3 as sql

from data.model.device import Device, Config, Potentiometer, PotentiometerConfig


class DeviceRepository:
    def __init__(self, filename: str):
        self._conn = sql.connect(filename, check_same_thread=False)

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

    async def create_potentiometer_config(self, value: str, potentiometer_id: int, config_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO potentiometer_configs (value, potentiometer_id, config_id) VALUES (?, ?, ?)",
            (value, str(potentiometer_id), str(config_id))
        )
        self._conn.commit()

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

    async def update_potentiometer_config(self, potentiometer_config_id: int, value: str):
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE potentiometer_configs SET value = ? WHERE id = ?",
            (value, str(potentiometer_config_id)),
        )
        self._conn.commit()

    def close(self):
        self._conn.close()
