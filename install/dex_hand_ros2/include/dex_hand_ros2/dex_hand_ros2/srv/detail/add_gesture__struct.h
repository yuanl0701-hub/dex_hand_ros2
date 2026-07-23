// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dex_hand_ros2:srv/AddGesture.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__STRUCT_H_
#define DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'name'
// Member 'description'
#include "rosidl_runtime_c/string.h"
// Member 'positions'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in srv/AddGesture in the package dex_hand_ros2.
typedef struct dex_hand_ros2__srv__AddGesture_Request
{
  rosidl_runtime_c__String name;
  /// 电机目标位置
  rosidl_runtime_c__int32__Sequence positions;
  rosidl_runtime_c__String description;
  double duration;
} dex_hand_ros2__srv__AddGesture_Request;

// Struct for a sequence of dex_hand_ros2__srv__AddGesture_Request.
typedef struct dex_hand_ros2__srv__AddGesture_Request__Sequence
{
  dex_hand_ros2__srv__AddGesture_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__srv__AddGesture_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/AddGesture in the package dex_hand_ros2.
typedef struct dex_hand_ros2__srv__AddGesture_Response
{
  bool success;
  rosidl_runtime_c__String message;
} dex_hand_ros2__srv__AddGesture_Response;

// Struct for a sequence of dex_hand_ros2__srv__AddGesture_Response.
typedef struct dex_hand_ros2__srv__AddGesture_Response__Sequence
{
  dex_hand_ros2__srv__AddGesture_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dex_hand_ros2__srv__AddGesture_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__STRUCT_H_
