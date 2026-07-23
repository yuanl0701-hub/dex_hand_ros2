// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from dex_hand_ros2:msg/GestureCmd.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__STRUCT_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__dex_hand_ros2__msg__GestureCmd __attribute__((deprecated))
#else
# define DEPRECATED__dex_hand_ros2__msg__GestureCmd __declspec(deprecated)
#endif

namespace dex_hand_ros2
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct GestureCmd_
{
  using Type = GestureCmd_<ContainerAllocator>;

  explicit GestureCmd_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->gesture = "";
      this->speed = 0.0f;
    }
  }

  explicit GestureCmd_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : gesture(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->gesture = "";
      this->speed = 0.0f;
    }
  }

  // field types and members
  using _gesture_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _gesture_type gesture;
  using _speed_type =
    float;
  _speed_type speed;

  // setters for named parameter idiom
  Type & set__gesture(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->gesture = _arg;
    return *this;
  }
  Type & set__speed(
    const float & _arg)
  {
    this->speed = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    dex_hand_ros2::msg::GestureCmd_<ContainerAllocator> *;
  using ConstRawPtr =
    const dex_hand_ros2::msg::GestureCmd_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::msg::GestureCmd_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::msg::GestureCmd_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__dex_hand_ros2__msg__GestureCmd
    std::shared_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__dex_hand_ros2__msg__GestureCmd
    std::shared_ptr<dex_hand_ros2::msg::GestureCmd_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GestureCmd_ & other) const
  {
    if (this->gesture != other.gesture) {
      return false;
    }
    if (this->speed != other.speed) {
      return false;
    }
    return true;
  }
  bool operator!=(const GestureCmd_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GestureCmd_

// alias to use template instance with default allocator
using GestureCmd =
  dex_hand_ros2::msg::GestureCmd_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__STRUCT_HPP_
