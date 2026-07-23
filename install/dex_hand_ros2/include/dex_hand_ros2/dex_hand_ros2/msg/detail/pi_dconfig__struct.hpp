// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from dex_hand_ros2:msg/PIDconfig.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__STRUCT_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__dex_hand_ros2__msg__PIDconfig __attribute__((deprecated))
#else
# define DEPRECATED__dex_hand_ros2__msg__PIDconfig __declspec(deprecated)
#endif

namespace dex_hand_ros2
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct PIDconfig_
{
  using Type = PIDconfig_<ContainerAllocator>;

  explicit PIDconfig_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor_id = 0l;
      this->kp = 0.0f;
      this->ki = 0.0f;
      this->kd = 0.0f;
    }
  }

  explicit PIDconfig_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor_id = 0l;
      this->kp = 0.0f;
      this->ki = 0.0f;
      this->kd = 0.0f;
    }
  }

  // field types and members
  using _motor_id_type =
    int32_t;
  _motor_id_type motor_id;
  using _kp_type =
    float;
  _kp_type kp;
  using _ki_type =
    float;
  _ki_type ki;
  using _kd_type =
    float;
  _kd_type kd;

  // setters for named parameter idiom
  Type & set__motor_id(
    const int32_t & _arg)
  {
    this->motor_id = _arg;
    return *this;
  }
  Type & set__kp(
    const float & _arg)
  {
    this->kp = _arg;
    return *this;
  }
  Type & set__ki(
    const float & _arg)
  {
    this->ki = _arg;
    return *this;
  }
  Type & set__kd(
    const float & _arg)
  {
    this->kd = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    dex_hand_ros2::msg::PIDconfig_<ContainerAllocator> *;
  using ConstRawPtr =
    const dex_hand_ros2::msg::PIDconfig_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::msg::PIDconfig_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::msg::PIDconfig_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__dex_hand_ros2__msg__PIDconfig
    std::shared_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__dex_hand_ros2__msg__PIDconfig
    std::shared_ptr<dex_hand_ros2::msg::PIDconfig_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PIDconfig_ & other) const
  {
    if (this->motor_id != other.motor_id) {
      return false;
    }
    if (this->kp != other.kp) {
      return false;
    }
    if (this->ki != other.ki) {
      return false;
    }
    if (this->kd != other.kd) {
      return false;
    }
    return true;
  }
  bool operator!=(const PIDconfig_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PIDconfig_

// alias to use template instance with default allocator
using PIDconfig =
  dex_hand_ros2::msg::PIDconfig_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__STRUCT_HPP_
