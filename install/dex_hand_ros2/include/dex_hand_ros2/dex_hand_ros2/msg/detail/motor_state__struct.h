// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dex_hand_ros2:msg/MotorState.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__STRUCT_H_
#define DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/MotorState in the package dex_hand_ros2.
typedef struct dex_hand_ros2__msg__MotorState
{
  /// 电机ID（1-6）
  int32_t motor_id;
  /// 电机当前位置
  int32_t position;
  /// 电机当前速度（可选，暂用不到）
  float velocity;
  /// 电机连接状态
  bool connected;
} dex_hand_ros2__msg__MotorState;

// Struct for a sequence of dex_hand_ros2__msg__MotorState.
typedef struct dex_hand_ros2__msg__MotorState__Sequence
{
  dex_hand_ros2__msg__MotorState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__msg__MotorState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__STRUCT_H_
