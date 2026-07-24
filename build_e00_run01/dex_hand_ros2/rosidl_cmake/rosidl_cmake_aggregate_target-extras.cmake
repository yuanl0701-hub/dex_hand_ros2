# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target dex_hand_ros2::dex_hand_ros2
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${dex_hand_ros2_TARGETS}.
if(dex_hand_ros2_TARGETS AND NOT TARGET dex_hand_ros2::dex_hand_ros2)
  add_library(dex_hand_ros2::dex_hand_ros2 INTERFACE IMPORTED)
  set_target_properties(dex_hand_ros2::dex_hand_ros2 PROPERTIES
    INTERFACE_LINK_LIBRARIES "${dex_hand_ros2_TARGETS}")
endif()
