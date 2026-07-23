# dex_hand_ros2/msg/PIDConfig.msg
int32 motor_id  # 电机ID（1-6）
float32 kp      # 比例系数
float32 ki      # 积分系数
float32 kd      # 微分系数