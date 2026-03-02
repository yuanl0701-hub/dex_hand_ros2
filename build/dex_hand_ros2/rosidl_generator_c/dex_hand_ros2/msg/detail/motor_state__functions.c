// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from dex_hand_ros2:msg/MotorState.idl
// generated code does not contain a copyright notice
#include "dex_hand_ros2/msg/detail/motor_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
dex_hand_ros2__msg__MotorState__init(dex_hand_ros2__msg__MotorState * msg)
{
  if (!msg) {
    return false;
  }
  // motor_id
  // position
  // velocity
  // connected
  return true;
}

void
dex_hand_ros2__msg__MotorState__fini(dex_hand_ros2__msg__MotorState * msg)
{
  if (!msg) {
    return;
  }
  // motor_id
  // position
  // velocity
  // connected
}

bool
dex_hand_ros2__msg__MotorState__are_equal(const dex_hand_ros2__msg__MotorState * lhs, const dex_hand_ros2__msg__MotorState * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // motor_id
  if (lhs->motor_id != rhs->motor_id) {
    return false;
  }
  // position
  if (lhs->position != rhs->position) {
    return false;
  }
  // velocity
  if (lhs->velocity != rhs->velocity) {
    return false;
  }
  // connected
  if (lhs->connected != rhs->connected) {
    return false;
  }
  return true;
}

bool
dex_hand_ros2__msg__MotorState__copy(
  const dex_hand_ros2__msg__MotorState * input,
  dex_hand_ros2__msg__MotorState * output)
{
  if (!input || !output) {
    return false;
  }
  // motor_id
  output->motor_id = input->motor_id;
  // position
  output->position = input->position;
  // velocity
  output->velocity = input->velocity;
  // connected
  output->connected = input->connected;
  return true;
}

dex_hand_ros2__msg__MotorState *
dex_hand_ros2__msg__MotorState__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__msg__MotorState * msg = (dex_hand_ros2__msg__MotorState *)allocator.allocate(sizeof(dex_hand_ros2__msg__MotorState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(dex_hand_ros2__msg__MotorState));
  bool success = dex_hand_ros2__msg__MotorState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
dex_hand_ros2__msg__MotorState__destroy(dex_hand_ros2__msg__MotorState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    dex_hand_ros2__msg__MotorState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
dex_hand_ros2__msg__MotorState__Sequence__init(dex_hand_ros2__msg__MotorState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__msg__MotorState * data = NULL;

  if (size) {
    data = (dex_hand_ros2__msg__MotorState *)allocator.zero_allocate(size, sizeof(dex_hand_ros2__msg__MotorState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = dex_hand_ros2__msg__MotorState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        dex_hand_ros2__msg__MotorState__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
dex_hand_ros2__msg__MotorState__Sequence__fini(dex_hand_ros2__msg__MotorState__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      dex_hand_ros2__msg__MotorState__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

dex_hand_ros2__msg__MotorState__Sequence *
dex_hand_ros2__msg__MotorState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__msg__MotorState__Sequence * array = (dex_hand_ros2__msg__MotorState__Sequence *)allocator.allocate(sizeof(dex_hand_ros2__msg__MotorState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = dex_hand_ros2__msg__MotorState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
dex_hand_ros2__msg__MotorState__Sequence__destroy(dex_hand_ros2__msg__MotorState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    dex_hand_ros2__msg__MotorState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
dex_hand_ros2__msg__MotorState__Sequence__are_equal(const dex_hand_ros2__msg__MotorState__Sequence * lhs, const dex_hand_ros2__msg__MotorState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!dex_hand_ros2__msg__MotorState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
dex_hand_ros2__msg__MotorState__Sequence__copy(
  const dex_hand_ros2__msg__MotorState__Sequence * input,
  dex_hand_ros2__msg__MotorState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(dex_hand_ros2__msg__MotorState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    dex_hand_ros2__msg__MotorState * data =
      (dex_hand_ros2__msg__MotorState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!dex_hand_ros2__msg__MotorState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          dex_hand_ros2__msg__MotorState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!dex_hand_ros2__msg__MotorState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
