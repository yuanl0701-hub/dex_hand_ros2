// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from dex_hand_ros2:srv/RunGesturePid.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__RUN_GESTURE_PID__STRUCT_HPP_
#define DEX_HAND_ROS2__SRV__DETAIL__RUN_GESTURE_PID__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Request __attribute__((deprecated))
#else
# define DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Request __declspec(deprecated)
#endif

namespace dex_hand_ros2
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RunGesturePid_Request_
{
  using Type = RunGesturePid_Request_<ContainerAllocator>;

  explicit RunGesturePid_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->gesture_name = "";
    }
  }

  explicit RunGesturePid_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : gesture_name(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->gesture_name = "";
    }
  }

  // field types and members
  using _gesture_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _gesture_name_type gesture_name;

  // setters for named parameter idiom
  Type & set__gesture_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->gesture_name = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Request
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Request
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RunGesturePid_Request_ & other) const
  {
    if (this->gesture_name != other.gesture_name) {
      return false;
    }
    return true;
  }
  bool operator!=(const RunGesturePid_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RunGesturePid_Request_

// alias to use template instance with default allocator
using RunGesturePid_Request =
  dex_hand_ros2::srv::RunGesturePid_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace dex_hand_ros2


#ifndef _WIN32
# define DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Response __attribute__((deprecated))
#else
# define DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Response __declspec(deprecated)
#endif

namespace dex_hand_ros2
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RunGesturePid_Response_
{
  using Type = RunGesturePid_Response_<ContainerAllocator>;

  explicit RunGesturePid_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit RunGesturePid_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Response
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__dex_hand_ros2__srv__RunGesturePid_Response
    std::shared_ptr<dex_hand_ros2::srv::RunGesturePid_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RunGesturePid_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const RunGesturePid_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RunGesturePid_Response_

// alias to use template instance with default allocator
using RunGesturePid_Response =
  dex_hand_ros2::srv::RunGesturePid_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace dex_hand_ros2

namespace dex_hand_ros2
{

namespace srv
{

struct RunGesturePid
{
  using Request = dex_hand_ros2::srv::RunGesturePid_Request;
  using Response = dex_hand_ros2::srv::RunGesturePid_Response;
};

}  // namespace srv

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__SRV__DETAIL__RUN_GESTURE_PID__STRUCT_HPP_
