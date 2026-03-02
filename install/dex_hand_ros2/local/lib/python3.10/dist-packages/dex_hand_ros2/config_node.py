#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from .hand_driver import MPD20Driver

class DexHandConfigNode(Node):
    def __init__(self):
        super().__init__("dex_hand_config_node")
        
        # 声明参数
        self.declare_parameter("serial_port", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 115200)
        
        # 获取参数
        port = self.get_parameter("serial_port").get_parameter_value().string_value
        baudrate = self.get_parameter("baudrate").get_parameter_value().integer_value
        
        # 初始化驱动
        self.driver = MPD20Driver(port=port, baudrate=baudrate)
        if not self.driver.connect():
            self.get_logger().error(f"配置节点串口连接失败：{port}")
            return
        self.get_logger().info(f"配置节点连接成功：{port}（波特率：{baudrate})")

        # 注册配置服务
        self.change_id_srv = self.create_service(
            Trigger, "/dex_hand/change_id", self.change_id_callback
        )
        self.change_baud_srv = self.create_service(
            Trigger, "/dex_hand/change_baud", self.change_baud_callback
        )

    def change_id_callback(self, request, response):
        """修改电机ID服务(参数格式:old_id>new_id,例如 1>2)"""
        try:
            old_id, new_id = map(int, request.message.split('>'))
            if not (1 <= old_id <= 255 and 1 <= new_id <= 255):
                response.success = False
                response.message = "ID必须是1-255之间的整数"
                return response
            if self.driver.change_id(old_id, new_id):
                response.success = True
                response.message = f"电机ID修改指令已发送:{old_id} → {new_id}（需重启电机生效）"
            else:
                response.success = False
                response.message = "电机ID修改失败(检查电机是否在线)"
        except ValueError:
            response.success = False
            response.message = "参数格式错误!需传入:old_id>new_id(例如 1>2)"
        except Exception as e:
            response.success = False
            response.message = f"修改ID失败:{str(e)}"
        return response

    def change_baud_callback(self, request, response):
        """修改电机波特率服务(参数格式:target_id>new_baud,例如 1>115200)"""
        try:
            target_id, new_baud = map(int, request.message.split('>'))
            if not 1 <= target_id <= 255:
                response.success = False
                response.message = "电机ID必须是1-255之间的整数!"
                return response
            if self.driver.change_baudrate(target_id, new_baud):
                response.success = True
                response.message = f"波特率修改指令已发送:ID={target_id} → {new_baud}（需重启电机生效）"
            else:
                response.success = False
                response.message = f"波特率修改失败（支持的波特率：{list(self.driver.BAUD_MAP.keys())})"
        except ValueError:
            response.success = False
            response.message = "参数格式错误!需传入:target_id>new_baud(例如 1>115200)"
        except Exception as e:
            response.success = False
            response.message = f"修改波特率失败：{str(e)}"
        return response

    def destroy_node(self):
        self.driver.disconnect()
        self.get_logger().info("配置节点串口已断开")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = DexHandConfigNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()