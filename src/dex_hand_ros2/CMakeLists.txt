cmake_minimum_required(VERSION 3.8)
project(dex_hand_ros2)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/hand_node
  scripts/config_node
  scripts/gesture_cli
  scripts/ros_experiment
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY config launch urdf rviz
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(core_tests test
    APPEND_ENV PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}
  )
endif()

ament_package()
