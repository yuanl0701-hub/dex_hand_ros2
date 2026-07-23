// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dex_hand_ros2:srv/ChangeBaud.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__CHANGE_BAUD__STRUCT_H_
#define DEX_HAND_ROS2__SRV__DETAIL__CHANGE_BAUD__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'command'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ChangeBaud in the package dex_hand_ros2.
typedef struct dex_hand_ros2__srv__ChangeBaud_Request
{
  /// 格式 "target_id>new_baud"
  rosidl_runtime_c__String command;
} dex_hand_ros2__srv__ChangeBaud_Request;

// Struct for a sequence of dex_hand_ros2__srv__ChangeBaud_Request.
typedef struct dex_hand_ros2__srv__ChangeBaud_Request__Sequence
{
  dex_hand_ros2__srv__ChangeBaud_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__srv__ChangeBaud_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ChangeBaud in the package dex_hand_ros2.
typedef struct dex_hand_ros2__srv__ChangeBaud_Response
{
  bool success;
  rosidl_runtime_c__String message;
} dex_hand_ros2__srv__ChangeBaud_Response;

// Struct for a sequence of dex_hand_ros2__srv__ChangeBaud_Response.
typedef struct dex_hand_ros2__srv__ChangeBaud_Response__Sequence
{
  dex_hand_ros2__srv__ChangeBaud_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__srv__ChangeBaud_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__SRV__DETAIL__CHANGE_BAUD__STRUCT_H_
