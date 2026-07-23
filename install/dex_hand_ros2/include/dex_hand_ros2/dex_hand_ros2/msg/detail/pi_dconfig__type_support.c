// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from dex_hand_ros2:msg/PIDconfig.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "dex_hand_ros2/msg/detail/pi_dconfig__rosidl_typesupport_introspection_c.h"
#include "dex_hand_ros2/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "dex_hand_ros2/msg/detail/pi_dconfig__functions.h"
#include "dex_hand_ros2/msg/detail/pi_dconfig__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  dex_hand_ros2__msg__PIDconfig__init(message_memory);
}

void dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_fini_function(void * message_memory)
{
  dex_hand_ros2__msg__PIDconfig__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_member_array[4] = {
  {
    "motor_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(dex_hand_ros2__msg__PIDconfig, motor_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "kp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(dex_hand_ros2__msg__PIDconfig, kp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "ki",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(dex_hand_ros2__msg__PIDconfig, ki),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "kd",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(dex_hand_ros2__msg__PIDconfig, kd),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_members = {
  "dex_hand_ros2__msg",  // message namespace
  "PIDconfig",  // message name
  4,  // number of fields
  sizeof(dex_hand_ros2__msg__PIDconfig),
  dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_member_array,  // message members
  dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_init_function,  // function to initialize message memory (memory has to be allocated)
  dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_type_support_handle = {
  0,
  &dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_dex_hand_ros2
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, dex_hand_ros2, msg, PIDconfig)() {
  if (!dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_type_support_handle.typesupport_identifier) {
    dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &dex_hand_ros2__msg__PIDconfig__rosidl_typesupport_introspection_c__PIDconfig_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
