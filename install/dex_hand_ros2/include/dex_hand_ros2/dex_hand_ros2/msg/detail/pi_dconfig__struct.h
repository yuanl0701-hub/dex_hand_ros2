// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dex_hand_ros2:msg/PIDconfig.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__STRUCT_H_
#define DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/PIDconfig in the package dex_hand_ros2.
/**
  * dex_hand_ros2/msg/PIDConfig.msg
 */
typedef struct dex_hand_ros2__msg__PIDconfig
{
  /// 电机ID（1-6）
  int32_t motor_id;
  /// 比例系数
  float kp;
  /// 积分系数
  float ki;
  /// 微分系数
  float kd;
} dex_hand_ros2__msg__PIDconfig;

// Struct for a sequence of dex_hand_ros2__msg__PIDconfig.
typedef struct dex_hand_ros2__msg__PIDconfig__Sequence
{
  dex_hand_ros2__msg__PIDconfig * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__msg__PIDconfig__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__STRUCT_H_
