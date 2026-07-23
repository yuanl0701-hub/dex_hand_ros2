// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from dex_hand_ros2:srv/RunGesturePid.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__RUN_GESTURE_PID__FUNCTIONS_H_
#define DEX_HAND_ROS2__SRV__DETAIL__RUN_GESTURE_PID__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "dex_hand_ros2/msg/rosidl_generator_c__visibility_control.h"

#include "dex_hand_ros2/srv/detail/run_gesture_pid__struct.h"

/// Initialize srv/RunGesturePid message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * dex_hand_ros2__srv__RunGesturePid_Request
 * )) before or use
 * dex_hand_ros2__srv__RunGesturePid_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Request__init(dex_hand_ros2__srv__RunGesturePid_Request * msg);

/// Finalize srv/RunGesturePid message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Request__fini(dex_hand_ros2__srv__RunGesturePid_Request * msg);

/// Create srv/RunGesturePid message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * dex_hand_ros2__srv__RunGesturePid_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
dex_hand_ros2__srv__RunGesturePid_Request *
dex_hand_ros2__srv__RunGesturePid_Request__create();

/// Destroy srv/RunGesturePid message.
/**
 * It calls
 * dex_hand_ros2__srv__RunGesturePid_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Request__destroy(dex_hand_ros2__srv__RunGesturePid_Request * msg);

/// Check for srv/RunGesturePid message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Request__are_equal(const dex_hand_ros2__srv__RunGesturePid_Request * lhs, const dex_hand_ros2__srv__RunGesturePid_Request * rhs);

/// Copy a srv/RunGesturePid message.
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
dex_hand_ros2__srv__RunGesturePid_Request__copy(
  const dex_hand_ros2__srv__RunGesturePid_Request * input,
  dex_hand_ros2__srv__RunGesturePid_Request * output);

/// Initialize array of srv/RunGesturePid messages.
/**
 * It allocates the memory for the number of elements and calls
 * dex_hand_ros2__srv__RunGesturePid_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Request__Sequence__init(dex_hand_ros2__srv__RunGesturePid_Request__Sequence * array, size_t size);

/// Finalize array of srv/RunGesturePid messages.
/**
 * It calls
 * dex_hand_ros2__srv__RunGesturePid_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Request__Sequence__fini(dex_hand_ros2__srv__RunGesturePid_Request__Sequence * array);

/// Create array of srv/RunGesturePid messages.
/**
 * It allocates the memory for the array and calls
 * dex_hand_ros2__srv__RunGesturePid_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
dex_hand_ros2__srv__RunGesturePid_Request__Sequence *
dex_hand_ros2__srv__RunGesturePid_Request__Sequence__create(size_t size);

/// Destroy array of srv/RunGesturePid messages.
/**
 * It calls
 * dex_hand_ros2__srv__RunGesturePid_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Request__Sequence__destroy(dex_hand_ros2__srv__RunGesturePid_Request__Sequence * array);

/// Check for srv/RunGesturePid message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Request__Sequence__are_equal(const dex_hand_ros2__srv__RunGesturePid_Request__Sequence * lhs, const dex_hand_ros2__srv__RunGesturePid_Request__Sequence * rhs);

/// Copy an array of srv/RunGesturePid messages.
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
dex_hand_ros2__srv__RunGesturePid_Request__Sequence__copy(
  const dex_hand_ros2__srv__RunGesturePid_Request__Sequence * input,
  dex_hand_ros2__srv__RunGesturePid_Request__Sequence * output);

/// Initialize srv/RunGesturePid message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * dex_hand_ros2__srv__RunGesturePid_Response
 * )) before or use
 * dex_hand_ros2__srv__RunGesturePid_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Response__init(dex_hand_ros2__srv__RunGesturePid_Response * msg);

/// Finalize srv/RunGesturePid message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Response__fini(dex_hand_ros2__srv__RunGesturePid_Response * msg);

/// Create srv/RunGesturePid message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * dex_hand_ros2__srv__RunGesturePid_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
dex_hand_ros2__srv__RunGesturePid_Response *
dex_hand_ros2__srv__RunGesturePid_Response__create();

/// Destroy srv/RunGesturePid message.
/**
 * It calls
 * dex_hand_ros2__srv__RunGesturePid_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Response__destroy(dex_hand_ros2__srv__RunGesturePid_Response * msg);

/// Check for srv/RunGesturePid message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Response__are_equal(const dex_hand_ros2__srv__RunGesturePid_Response * lhs, const dex_hand_ros2__srv__RunGesturePid_Response * rhs);

/// Copy a srv/RunGesturePid message.
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
dex_hand_ros2__srv__RunGesturePid_Response__copy(
  const dex_hand_ros2__srv__RunGesturePid_Response * input,
  dex_hand_ros2__srv__RunGesturePid_Response * output);

/// Initialize array of srv/RunGesturePid messages.
/**
 * It allocates the memory for the number of elements and calls
 * dex_hand_ros2__srv__RunGesturePid_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Response__Sequence__init(dex_hand_ros2__srv__RunGesturePid_Response__Sequence * array, size_t size);

/// Finalize array of srv/RunGesturePid messages.
/**
 * It calls
 * dex_hand_ros2__srv__RunGesturePid_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Response__Sequence__fini(dex_hand_ros2__srv__RunGesturePid_Response__Sequence * array);

/// Create array of srv/RunGesturePid messages.
/**
 * It allocates the memory for the array and calls
 * dex_hand_ros2__srv__RunGesturePid_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
dex_hand_ros2__srv__RunGesturePid_Response__Sequence *
dex_hand_ros2__srv__RunGesturePid_Response__Sequence__create(size_t size);

/// Destroy array of srv/RunGesturePid messages.
/**
 * It calls
 * dex_hand_ros2__srv__RunGesturePid_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
void
dex_hand_ros2__srv__RunGesturePid_Response__Sequence__destroy(dex_hand_ros2__srv__RunGesturePid_Response__Sequence * array);

/// Check for srv/RunGesturePid message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_dex_hand_ros2
bool
dex_hand_ros2__srv__RunGesturePid_Response__Sequence__are_equal(const dex_hand_ros2__srv__RunGesturePid_Response__Sequence * lhs, const dex_hand_ros2__srv__RunGesturePid_Response__Sequence * rhs);

/// Copy an array of srv/RunGesturePid messages.
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
dex_hand_ros2__srv__RunGesturePid_Response__Sequence__copy(
  const dex_hand_ros2__srv__RunGesturePid_Response__Sequence * input,
  dex_hand_ros2__srv__RunGesturePid_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // DEX_HAND_ROS2__SRV__DETAIL__RUN_GESTURE_PID__FUNCTIONS_H_
