// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from dex_hand_ros2:srv/AddGesture.idl
// generated code does not contain a copyright notice
#include "dex_hand_ros2/srv/detail/add_gesture__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `name`
// Member `description`
#include "rosidl_runtime_c/string_functions.h"
// Member `positions`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
dex_hand_ros2__srv__AddGesture_Request__init(dex_hand_ros2__srv__AddGesture_Request * msg)
{
  if (!msg) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__init(&msg->name)) {
    dex_hand_ros2__srv__AddGesture_Request__fini(msg);
    return false;
  }
  // positions
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->positions, 0)) {
    dex_hand_ros2__srv__AddGesture_Request__fini(msg);
    return false;
  }
  // description
  if (!rosidl_runtime_c__String__init(&msg->description)) {
    dex_hand_ros2__srv__AddGesture_Request__fini(msg);
    return false;
  }
  // duration
  return true;
}

void
dex_hand_ros2__srv__AddGesture_Request__fini(dex_hand_ros2__srv__AddGesture_Request * msg)
{
  if (!msg) {
    return;
  }
  // name
  rosidl_runtime_c__String__fini(&msg->name);
  // positions
  rosidl_runtime_c__int32__Sequence__fini(&msg->positions);
  // description
  rosidl_runtime_c__String__fini(&msg->description);
  // duration
}

bool
dex_hand_ros2__srv__AddGesture_Request__are_equal(const dex_hand_ros2__srv__AddGesture_Request * lhs, const dex_hand_ros2__srv__AddGesture_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->name), &(rhs->name)))
  {
    return false;
  }
  // positions
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->positions), &(rhs->positions)))
  {
    return false;
  }
  // description
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->description), &(rhs->description)))
  {
    return false;
  }
  // duration
  if (lhs->duration != rhs->duration) {
    return false;
  }
  return true;
}

bool
dex_hand_ros2__srv__AddGesture_Request__copy(
  const dex_hand_ros2__srv__AddGesture_Request * input,
  dex_hand_ros2__srv__AddGesture_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__copy(
      &(input->name), &(output->name)))
  {
    return false;
  }
  // positions
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->positions), &(output->positions)))
  {
    return false;
  }
  // description
  if (!rosidl_runtime_c__String__copy(
      &(input->description), &(output->description)))
  {
    return false;
  }
  // duration
  output->duration = input->duration;
  return true;
}

dex_hand_ros2__srv__AddGesture_Request *
dex_hand_ros2__srv__AddGesture_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__srv__AddGesture_Request * msg = (dex_hand_ros2__srv__AddGesture_Request *)allocator.allocate(sizeof(dex_hand_ros2__srv__AddGesture_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(dex_hand_ros2__srv__AddGesture_Request));
  bool success = dex_hand_ros2__srv__AddGesture_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
dex_hand_ros2__srv__AddGesture_Request__destroy(dex_hand_ros2__srv__AddGesture_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    dex_hand_ros2__srv__AddGesture_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
dex_hand_ros2__srv__AddGesture_Request__Sequence__init(dex_hand_ros2__srv__AddGesture_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__srv__AddGesture_Request * data = NULL;

  if (size) {
    data = (dex_hand_ros2__srv__AddGesture_Request *)allocator.zero_allocate(size, sizeof(dex_hand_ros2__srv__AddGesture_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = dex_hand_ros2__srv__AddGesture_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        dex_hand_ros2__srv__AddGesture_Request__fini(&data[i - 1]);
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
dex_hand_ros2__srv__AddGesture_Request__Sequence__fini(dex_hand_ros2__srv__AddGesture_Request__Sequence * array)
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
      dex_hand_ros2__srv__AddGesture_Request__fini(&array->data[i]);
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

dex_hand_ros2__srv__AddGesture_Request__Sequence *
dex_hand_ros2__srv__AddGesture_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__srv__AddGesture_Request__Sequence * array = (dex_hand_ros2__srv__AddGesture_Request__Sequence *)allocator.allocate(sizeof(dex_hand_ros2__srv__AddGesture_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = dex_hand_ros2__srv__AddGesture_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
dex_hand_ros2__srv__AddGesture_Request__Sequence__destroy(dex_hand_ros2__srv__AddGesture_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    dex_hand_ros2__srv__AddGesture_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
dex_hand_ros2__srv__AddGesture_Request__Sequence__are_equal(const dex_hand_ros2__srv__AddGesture_Request__Sequence * lhs, const dex_hand_ros2__srv__AddGesture_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!dex_hand_ros2__srv__AddGesture_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
dex_hand_ros2__srv__AddGesture_Request__Sequence__copy(
  const dex_hand_ros2__srv__AddGesture_Request__Sequence * input,
  dex_hand_ros2__srv__AddGesture_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(dex_hand_ros2__srv__AddGesture_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    dex_hand_ros2__srv__AddGesture_Request * data =
      (dex_hand_ros2__srv__AddGesture_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!dex_hand_ros2__srv__AddGesture_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          dex_hand_ros2__srv__AddGesture_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!dex_hand_ros2__srv__AddGesture_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
dex_hand_ros2__srv__AddGesture_Response__init(dex_hand_ros2__srv__AddGesture_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    dex_hand_ros2__srv__AddGesture_Response__fini(msg);
    return false;
  }
  return true;
}

void
dex_hand_ros2__srv__AddGesture_Response__fini(dex_hand_ros2__srv__AddGesture_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
dex_hand_ros2__srv__AddGesture_Response__are_equal(const dex_hand_ros2__srv__AddGesture_Response * lhs, const dex_hand_ros2__srv__AddGesture_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
dex_hand_ros2__srv__AddGesture_Response__copy(
  const dex_hand_ros2__srv__AddGesture_Response * input,
  dex_hand_ros2__srv__AddGesture_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

dex_hand_ros2__srv__AddGesture_Response *
dex_hand_ros2__srv__AddGesture_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__srv__AddGesture_Response * msg = (dex_hand_ros2__srv__AddGesture_Response *)allocator.allocate(sizeof(dex_hand_ros2__srv__AddGesture_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(dex_hand_ros2__srv__AddGesture_Response));
  bool success = dex_hand_ros2__srv__AddGesture_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
dex_hand_ros2__srv__AddGesture_Response__destroy(dex_hand_ros2__srv__AddGesture_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    dex_hand_ros2__srv__AddGesture_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
dex_hand_ros2__srv__AddGesture_Response__Sequence__init(dex_hand_ros2__srv__AddGesture_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__srv__AddGesture_Response * data = NULL;

  if (size) {
    data = (dex_hand_ros2__srv__AddGesture_Response *)allocator.zero_allocate(size, sizeof(dex_hand_ros2__srv__AddGesture_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = dex_hand_ros2__srv__AddGesture_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        dex_hand_ros2__srv__AddGesture_Response__fini(&data[i - 1]);
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
dex_hand_ros2__srv__AddGesture_Response__Sequence__fini(dex_hand_ros2__srv__AddGesture_Response__Sequence * array)
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
      dex_hand_ros2__srv__AddGesture_Response__fini(&array->data[i]);
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

dex_hand_ros2__srv__AddGesture_Response__Sequence *
dex_hand_ros2__srv__AddGesture_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  dex_hand_ros2__srv__AddGesture_Response__Sequence * array = (dex_hand_ros2__srv__AddGesture_Response__Sequence *)allocator.allocate(sizeof(dex_hand_ros2__srv__AddGesture_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = dex_hand_ros2__srv__AddGesture_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
dex_hand_ros2__srv__AddGesture_Response__Sequence__destroy(dex_hand_ros2__srv__AddGesture_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    dex_hand_ros2__srv__AddGesture_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
dex_hand_ros2__srv__AddGesture_Response__Sequence__are_equal(const dex_hand_ros2__srv__AddGesture_Response__Sequence * lhs, const dex_hand_ros2__srv__AddGesture_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!dex_hand_ros2__srv__AddGesture_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
dex_hand_ros2__srv__AddGesture_Response__Sequence__copy(
  const dex_hand_ros2__srv__AddGesture_Response__Sequence * input,
  dex_hand_ros2__srv__AddGesture_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(dex_hand_ros2__srv__AddGesture_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    dex_hand_ros2__srv__AddGesture_Response * data =
      (dex_hand_ros2__srv__AddGesture_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!dex_hand_ros2__srv__AddGesture_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          dex_hand_ros2__srv__AddGesture_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!dex_hand_ros2__srv__AddGesture_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
