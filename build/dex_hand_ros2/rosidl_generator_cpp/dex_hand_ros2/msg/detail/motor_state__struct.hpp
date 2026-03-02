// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from dex_hand_ros2:msg/MotorState.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__STRUCT_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__dex_hand_ros2__msg__MotorState __attribute__((deprecated))
#else
# define DEPRECATED__dex_hand_ros2__msg__MotorState __declspec(deprecated)
#endif

namespace dex_hand_ros2
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MotorState_
{
  using Type = MotorState_<ContainerAllocator>;

  explicit MotorState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor_id = 0l;
      this->position = 0l;
      this->velocity = 0.0f;
      this->connected = false;
    }
  }

  explicit MotorState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor_id = 0l;
      this->position = 0l;
      this->velocity = 0.0f;
      this->connected = false;
    }
  }

  // field types and members
  using _motor_id_type =
    int32_t;
  _motor_id_type motor_id;
  using _position_type =
    int32_t;
  _position_type position;
  using _velocity_type =
    float;
  _velocity_type velocity;
  using _connected_type =
    bool;
  _connected_type connected;

  // setters for named parameter idiom
  Type & set__motor_id(
    const int32_t & _arg)
  {
    this->motor_id = _arg;
    return *this;
  }
  Type & set__position(
    const int32_t & _arg)
  {
    this->position = _arg;
    return *this;
  }
  Type & set__velocity(
    const float & _arg)
  {
    this->velocity = _arg;
    return *this;
  }
  Type & set__connected(
    const bool & _arg)
  {
    this->connected = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    dex_hand_ros2::msg::MotorState_<ContainerAllocator> *;
  using ConstRawPtr =
    const dex_hand_ros2::msg::MotorState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::msg::MotorState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::msg::MotorState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__dex_hand_ros2__msg__MotorState
    std::shared_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__dex_hand_ros2__msg__MotorState
    std::shared_ptr<dex_hand_ros2::msg::MotorState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MotorState_ & other) const
  {
    if (this->motor_id != other.motor_id) {
      return false;
    }
    if (this->position != other.position) {
      return false;
    }
    if (this->velocity != other.velocity) {
      return false;
    }
    if (this->connected != other.connected) {
      return false;
    }
    return true;
  }
  bool operator!=(const MotorState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MotorState_

// alias to use template instance with default allocator
using MotorState =
  dex_hand_ros2::msg::MotorState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__STRUCT_HPP_
