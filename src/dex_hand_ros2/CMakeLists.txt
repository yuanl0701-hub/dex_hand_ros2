cmake_minimum_required(VERSION 3.8)
project(dex_hand_ros2)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
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

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/hand_node
  scripts/config_node
  scripts/gesture_cli
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(core_tests test
    APPEND_ENV PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}
  )
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
