// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dex_hand_ros2:srv/ChangeId.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__CHANGE_ID__STRUCT_H_
#define DEX_HAND_ROS2__SRV__DETAIL__CHANGE_ID__STRUCT_H_

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

/// Struct defined in srv/ChangeId in the package dex_hand_ros2.
typedef struct dex_hand_ros2__srv__ChangeId_Request
{
  /// 请求：格式 "old_id>new_id"
  rosidl_runtime_c__String command;
} dex_hand_ros2__srv__ChangeId_Request;

// Struct for a sequence of dex_hand_ros2__srv__ChangeId_Request.
typedef struct dex_hand_ros2__srv__ChangeId_Request__Sequence
{
  dex_hand_ros2__srv__ChangeId_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__srv__ChangeId_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ChangeId in the package dex_hand_ros2.
typedef struct dex_hand_ros2__srv__ChangeId_Response
{
  /// 响应：是否成功
  bool success;
  /// 响应：提示信息
  rosidl_runtime_c__String message;
} dex_hand_ros2__srv__ChangeId_Response;

// Struct for a sequence of dex_hand_ros2__srv__ChangeId_Response.
typedef struct dex_hand_ros2__srv__ChangeId_Response__Sequence
{
  dex_hand_ros2__srv__ChangeId_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__srv__ChangeId_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__SRV__DETAIL__CHANGE_ID__STRUCT_H_
