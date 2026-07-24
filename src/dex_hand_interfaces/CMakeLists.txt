cmake_minimum_required(VERSION 3.8)
project(dex_hand_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/GestureCmd.msg"
  "msg/MotorState.msg"
  "msg/PIDconfig.msg"
  "srv/AddGesture.srv"
  "srv/ChangeBaud.srv"
  "srv/ChangeId.srv"
  "srv/RunGesturePid.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
