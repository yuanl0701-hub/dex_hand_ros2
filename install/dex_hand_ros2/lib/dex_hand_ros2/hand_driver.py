#!/usr/bin/env python3
import serial
import struct
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

# 通用电机驱动抽象类
class GenericMotorDriver(ABC):
    @abstractmethod
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        pass

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def set_single_position(self, motor_id: int, position: int) -> bool:
        pass

    @abstractmethod
    def set_multiple_positions(self, positions: Dict[int, int]) -> bool:
        pass

    @abstractmethod
    def get_position(self, motor_id: int) -> Optional[int]:
        pass

    @abstractmethod
    def get_multiple_positions(self, motor_ids: List[int]) -> Dict[int, Optional[int]]:
        pass

    @abstractmethod
    def change_id(self, old_id: int, new_id: int) -> bool:
        pass

    @abstractmethod
    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        pass

# Modbus RTU协议实现（适配MPD20电机）
class ModbusRTUProtocol:
    READ_HOLDING_REGISTERS = 0x03
    WRITE_SINGLE_REGISTER = 0x06

    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None

    def connect(self) -> bool:
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=0.5
            )
            return self.ser.is_open
        except Exception as e:
            print(f"串口连接失败：{e}")
            return False

    def disconnect(self) -> bool:
        if self.ser:
            self.ser.close()
            self.ser = None
        return True

    def is_connected(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def calculate_crc(self, data: bytes) -> int:
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF

    def build_frame(self, content: bytes) -> bytes:
        crc = self.calculate_crc(content)
        return content + struct.pack('<H', crc)

    def send(self, data: bytes) -> None:
        if self.ser:
            self.ser.write(data)
            self.ser.flush()

    def receive(self, size: int) -> bytes:
        if self.ser:
            return self.ser.read(size)
        return b''

# MPD20电机驱动实现
class MPD20Driver(GenericMotorDriver):
    REG_ID = 0x0000
    REG_BAUD = 0x0001
    REG_POS = 0x0002
    BAUD_MAP = {115200:4, 38400:7, 19200:8, 9600:9, 4800:10}

    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self._comm = ModbusRTUProtocol(port, baudrate)

    def connect(self) -> bool:
        return self._comm.connect()

    def disconnect(self) -> bool:
        return self._comm.disconnect()

    def is_connected(self) -> bool:
        return self._comm.is_connected()

    def set_single_position(self, motor_id: int, position: int) -> bool:
        try:
            content = bytes([motor_id, self._comm.WRITE_SINGLE_REGISTER, 
                            (self.REG_POS >> 8) & 0xFF, self.REG_POS & 0xFF,
                            (position >> 8) & 0xFF, position & 0xFF])
            frame = self._comm.build_frame(content)
            self._comm.send(frame)
            return True
        except Exception as e:
            print(f"设置电机{motor_id}位置失败：{e}")
            return False

    def set_multiple_positions(self, positions: Dict[int, int]) -> bool:
        for motor_id, pos in positions.items():
            self.set_single_position(motor_id, pos)
        return True

    def get_position(self, motor_id: int) -> Optional[int]:
        try:
            content = bytes([motor_id, self._comm.READ_HOLDING_REGISTERS,
                            (self.REG_POS >> 8) & 0xFF, self.REG_POS & 0xFF,
                            0x00, 0x01])
            frame = self._comm.build_frame(content)
            self._comm.send(frame)
            resp = self._comm.receive(7)
            if len(resp) == 7 and resp[0] == motor_id:
                return (resp[3] << 8) | resp[4]
            return None
        except Exception as e:
            print(f"读取电机{motor_id}位置失败：{e}")
            return None

    def get_multiple_positions(self, motor_ids: List[int]) -> Dict[int, Optional[int]]:
        return {mid: self.get_position(mid) for mid in motor_ids}

    def change_id(self, old_id: int, new_id: int) -> bool:
        try:
            content = bytes([old_id, self._comm.WRITE_SINGLE_REGISTER,
                            (self.REG_ID >> 8) & 0xFF, self.REG_ID & 0xFF,
                            0x00, new_id])
            frame = self._comm.build_frame(content)
            self._comm.send(frame)
            return True
        except Exception as e:
            print(f"修改电机ID失败:{e}")
            return False

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        if new_baud not in self.BAUD_MAP:
            print(f"不支持的波特率：{new_baud}，支持列表：{list(self.BAUD_MAP.keys())}")
            return False
        try:
            baud_code = self.BAUD_MAP[new_baud]
            content = bytes([target_id, self._comm.WRITE_SINGLE_REGISTER,
                            (self.REG_BAUD >> 8) & 0xFF, self.REG_BAUD & 0xFF,
                            0x00, baud_code])
            frame = self._comm.build_frame(content)
            self._comm.send(frame)
            return True
        except Exception as e:
            print(f"修改电机波特率失败：{e}")
            return False

# 机械手核心类（手势管理）
class GestureDefinition:
    def __init__(self, name: str, positions: Dict[int, int], 
                 description: str = "", duration: float = 0.5):
        self.name = name
        self.positions = positions
        self.description = description
        self.duration = duration

class RoboticHand:
    # 预定义手势（可根据你的机械手修改）
    PREDEFINED_GESTURES = {
        "open": GestureDefinition("open", {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100}, "张开手"),
        "fist": GestureDefinition("fist", {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, "握拳"),
        "vgesture": GestureDefinition("vgesture", {1: 100, 2: 0, 3: 100, 4: 0, 5: 0, 6: 0}, "V字手势"),
    }

    def __init__(self, driver: GenericMotorDriver):
        self._driver = driver
        self._custom_gestures: Dict[str, GestureDefinition] = {}

    @property
    def driver(self) -> GenericMotorDriver:
        return self._driver

    def run_gesture(self, gesture_name: str) -> bool:
        gesture = self._custom_gestures.get(gesture_name) or self.PREDEFINED_GESTURES.get(gesture_name)
        if not gesture:
            print(f"未找到手势：{gesture_name}")
            return False
        self._driver.set_multiple_positions(gesture.positions)
        return True

    def get_gesture_list(self) -> List[str]:
        return list(self.PREDEFINED_GESTURES.keys()) + list(self._custom_gestures.keys())

    def get_gesture_info(self, gesture_name: str) -> Optional[GestureDefinition]:
        return self._custom_gestures.get(gesture_name) or self.PREDEFINED_GESTURES.get(gesture_name)

    def add_gesture(self, name: str, positions: Dict[int, int], 
                    description: str = "", duration: float = 0.5) -> bool:
        self._custom_gestures[name] = GestureDefinition(name, positions, description, duration)
        return True

    def set_motor_position(self, motor_id: int, position: int) -> bool:
        return self._driver.set_single_position(motor_id, position)