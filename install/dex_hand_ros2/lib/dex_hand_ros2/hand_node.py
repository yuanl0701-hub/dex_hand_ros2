#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String, Int32MultiArray
from std_srvs.srv import Trigger
from dex_hand_ros2.msg import GestureCmd, MotorState
from .hand_driver import MPD20Driver, RoboticHand
import time
from typing import Dict

class DexHandROS2Node(Node):
    def __init__(self):
        super().__init__("dex_hand_node")
        
        # 1. 声明ROS2参数（可外部配置）
        self.declare_parameter("serial_port", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("status_pub_freq", 10.0)
        
        # 2. 获取参数值
        port = self.get_parameter("serial_port").get_parameter_value().string_value
        baudrate = self.get_parameter("baudrate").get_parameter_value().integer_value
        self.status_freq = self.get_parameter("status_pub_freq").get_parameter_value().double_value

        # 3. 初始化电机驱动和机械手
        self.driver = MPD20Driver(port=port, baudrate=baudrate)
        if not self.driver.connect():
            self.get_logger().error(f"串口连接失败：{port}(波特率：{baudrate})")
            return
        self.hand = RoboticHand(self.driver)
        self.get_logger().info(f"机械手连接成功：{port}(波特率：{baudrate})")

        # 4. 配置QoS（可靠传输，避免指令丢失）
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # 5. 初始化发布者
        self.status_pub = self.create_publisher(String, "/dex_hand/status", qos_profile)
        self.motor_state_pub = self.create_publisher(MotorState, "/dex_hand/motor_state", qos_profile)
        
        # 6. 初始化订阅者
        self.gesture_cmd_sub = self.create_subscription(
            GestureCmd, "/dex_hand/gesture_cmd", self.gesture_cmd_callback, qos_profile
        )
        self.motor_pos_sub = self.create_subscription(
            Int32MultiArray, "/dex_hand/motor_pos_cmd", self.motor_pos_callback, qos_profile
        )

        # 7. 初始化服务
        self.list_gestures_srv = self.create_service(
            Trigger, "/dex_hand/list_gestures", self.list_gestures_callback
        )
        self.demo_gestures_srv = self.create_service(
            Trigger, "/dex_hand/demo_gestures", self.demo_gestures_callback
        )
        self.add_gesture_srv = self.create_service(
            Trigger, "/dex_hand/add_gesture", self.add_gesture_callback
        )

        # 8. 状态发布定时器（每秒发布10次）
        self.status_timer = self.create_timer(1.0/self.status_freq, self.publish_status)

    def gesture_cmd_callback(self, msg: GestureCmd):
        """处理手势指令回调"""
        gesture_name = msg.gesture
        if self.hand.run_gesture(gesture_name):
            self.get_logger().info(f"执行手势成功：{gesture_name}")
        else:
            self.get_logger().error(f"执行手势失败：{gesture_name}（手势不存在）")

    def motor_pos_callback(self, msg: Int32MultiArray):
        """处理电机位置指令（格式：[motor_id, position])"""
        if len(msg.data) < 2:
            self.get_logger().error("电机指令格式错误！需传入 [motor_id, position]，例如 [1, 100]")
            return
        motor_id = msg.data[0]
        position = msg.data[1]
        if 1 <= motor_id <= 6 and 0 <= position <= 100:
            if self.hand.set_motor_position(motor_id, position):
                self.get_logger().info(f"设置电机{motor_id}位置成功：{position}")
            else:
                self.get_logger().error(f"设置电机{motor_id}位置失败")
        else:
            self.get_logger().error(f"参数非法!电机ID:1-6,位置:0-1009(当前:ID={motor_id}, 位置={position})")

    def list_gestures_callback(self, request, response):
        """列出手势服务回调"""
        gestures = self.hand.get_gesture_list()
        response.success = True
        response.message = ", ".join(gestures)
        return response

    def demo_gestures_callback(self, request, response):
        """演示所有手势服务回调"""
        try:
            gestures = self.hand.get_gesture_list()
            self.get_logger().info(f"开始演示手势（共{len(gestures)}个）：{gestures}")
            for g in gestures:
                self.hand.run_gesture(g)
                time.sleep(1.0)
            response.success = True
            response.message = f"手势演示完成！共执行 {len(gestures)} 个手势"
        except Exception as e:
            response.success = False
            response.message = f"手势演示失败：{str(e)}"
        return response

    def add_gesture_callback(self, request, response):
        """添加自定义手势服务回调(格式:name,p1,p2,p3,p4,p5,p6)"""
        try:
            args = request.message.split(',')
            if len(args) < 7:
                response.success = False
                response.message = "参数格式错误!需传入:name,p1,p2,p3,p4,p5,p6(例如:test,10,20,30,40,50,60)"
                return response
            name = args[0].strip()
            positions = {i+1: int(args[i+1]) for i in range(6)}
            # 校验位置范围
            for pos in positions.values():
                if not 0 <= pos <= 100:
                    response.success = False
                    response.message = "位置参数非法!需为0-100之间的整数"
                    return response
            self.hand.add_gesture(name, positions, "ROS2自定义手势")
            response.success = True
            response.message = f"添加手势成功：{name}（位置：{positions})"
        except ValueError:
            response.success = False
            response.message = "位置参数必须是整数！"
        except Exception as e:
            response.success = False
            response.message = f"添加手势失败：{str(e)}"
        return response

    def publish_status(self):
        """定时发布机械手状态"""
        # 发布整体状态
        status_msg = String()
        status_msg.data = f"连接状态：{self.driver.is_connected()}, 手势数量：{len(self.hand.get_gesture_list())}"
        self.status_pub.publish(status_msg)
        
        # 发布电机1的状态（可扩展为所有电机）
        motor_state = MotorState()
        motor_state.motor_id = 1
        motor_state.position = self.driver.get_position(1) or -1
        motor_state.connected = self.driver.is_connected()
        self.motor_state_pub.publish(motor_state)

    def destroy_node(self):
        """销毁节点时断开串口"""
        self.driver.disconnect()
        self.get_logger().info("机械手串口已断开，节点关闭")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = DexHandROS2Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("用户终止，开始关闭节点...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()