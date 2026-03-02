// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from dex_hand_ros2:msg/GestureCmd.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__FUNCTIONS_H_
#define DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "dex_hand_ros2/msg/rosidl_generator_c__visibility_control.h"

#include "dex_hand_ros2/msg/detail/gesture_cmd__struct.h"

/// Initialize msg/GestureCmd message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * dex_hand_ros2__msg__GestureCmd
 * )) before or use
 * dex_hand_ros2__msg__GestureCmd__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__msg__GestureCmd__init(dex_hand_ros2__msg__GestureCmd * msg);

/// Finalize msg/GestureCmd message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__msg__GestureCmd__fini(dex_hand_ros2__msg__GestureCmd * msg);

/// Create msg/GestureCmd message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * dex_hand_ros2__msg__GestureCmd__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
dex_hand_ros2__msg__GestureCmd *
dex_hand_ros2__msg__GestureCmd__create();

/// Destroy msg/GestureCmd message.
/**
 * It calls
 * dex_hand_ros2__msg__GestureCmd__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__msg__GestureCmd__destroy(dex_hand_ros2__msg__GestureCmd * msg);

/// Check for msg/GestureCmd message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__msg__GestureCmd__are_equal(const dex_hand_ros2__msg__GestureCmd * lhs, const dex_hand_ros2__msg__GestureCmd * rhs);

/// Copy a msg/GestureCmd message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__msg__GestureCmd__copy(
  const dex_hand_ros2__msg__GestureCmd * input,
  dex_hand_ros2__msg__GestureCmd * output);

/// Initialize array of msg/GestureCmd messages.
/**
 * It allocates the memory for the number of elements and calls
 * dex_hand_ros2__msg__GestureCmd__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__msg__GestureCmd__Sequence__init(dex_hand_ros2__msg__GestureCmd__Sequence * array, size_t size);

/// Finalize array of msg/GestureCmd messages.
/**
 * It calls
 * dex_hand_ros2__msg__GestureCmd__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__msg__GestureCmd__Sequence__fini(dex_hand_ros2__msg__GestureCmd__Sequence * array);

/// Create array of msg/GestureCmd messages.
/**
 * It allocates the memory for the array and calls
 * dex_hand_ros2__msg__GestureCmd__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
dex_hand_ros2__msg__GestureCmd__Sequence *
dex_hand_ros2__msg__GestureCmd__Sequence__create(size_t size);

/// Destroy array of msg/GestureCmd messages.
/**
 * It calls
 * dex_hand_ros2__msg__GestureCmd__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__msg__GestureCmd__Sequence__destroy(dex_hand_ros2__msg__GestureCmd__Sequence * array);

/// Check for msg/GestureCmd message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__msg__GestureCmd__Sequence__are_equal(const dex_hand_ros2__msg__GestureCmd__Sequence * lhs, const dex_hand_ros2__msg__GestureCmd__Sequence * rhs);

/// Copy an array of msg/GestureCmd messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__msg__GestureCmd__Sequence__copy(
  const dex_hand_ros2__msg__GestureCmd__Sequence * input,
  dex_hand_ros2__msg__GestureCmd__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__FUNCTIONS_H_
