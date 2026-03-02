// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dex_hand_ros2:msg/GestureCmd.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__STRUCT_H_
#define DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'gesture'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/GestureCmd in the package dex_hand_ros2.
typedef struct dex_hand_ros2__msg__GestureCmd
{
  /// 手势指令
  rosidl_runtime_c__String gesture;
  /// 执行速度（0.0~1.0
  float speed;
} dex_hand_ros2__msg__GestureCmd;

// Struct for a sequence of dex_hand_ros2__msg__GestureCmd.
typedef struct dex_hand_ros2__msg__GestureCmd__Sequence
{
  dex_hand_ros2__msg__GestureCmd * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__msg__GestureCmd__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__STRUCT_H_
