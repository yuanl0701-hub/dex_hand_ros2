// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from dex_hand_ros2:srv/AddGesture.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__BUILDER_HPP_
#define DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "dex_hand_ros2/srv/detail/add_gesture__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace dex_hand_ros2
{

namespace srv
{

namespace builder
{

class Init_AddGesture_Request_duration
{
public:
  explicit Init_AddGesture_Request_duration(::dex_hand_ros2::srv::AddGesture_Request & msg)
  : msg_(msg)
  {}
  ::dex_hand_ros2::srv::AddGesture_Request duration(::dex_hand_ros2::srv::AddGesture_Request::_duration_type arg)
  {
    msg_.duration = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::srv::AddGesture_Request msg_;
};

class Init_AddGesture_Request_description
{
public:
  explicit Init_AddGesture_Request_description(::dex_hand_ros2::srv::AddGesture_Request & msg)
  : msg_(msg)
  {}
  Init_AddGesture_Request_duration description(::dex_hand_ros2::srv::AddGesture_Request::_description_type arg)
  {
    msg_.description = std::move(arg);
    return Init_AddGesture_Request_duration(msg_);
  }

private:
  ::dex_hand_ros2::srv::AddGesture_Request msg_;
};

class Init_AddGesture_Request_positions
{
public:
  explicit Init_AddGesture_Request_positions(::dex_hand_ros2::srv::AddGesture_Request & msg)
  : msg_(msg)
  {}
  Init_AddGesture_Request_description positions(::dex_hand_ros2::srv::AddGesture_Request::_positions_type arg)
  {
    msg_.positions = std::move(arg);
    return Init_AddGesture_Request_description(msg_);
  }

private:
  ::dex_hand_ros2::srv::AddGesture_Request msg_;
};

class Init_AddGesture_Request_name
{
public:
  Init_AddGesture_Request_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_AddGesture_Request_positions name(::dex_hand_ros2::srv::AddGesture_Request::_name_type arg)
  {
    msg_.name = std::move(arg);
    return Init_AddGesture_Request_positions(msg_);
  }

private:
  ::dex_hand_ros2::srv::AddGesture_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::srv::AddGesture_Request>()
{
  return dex_hand_ros2::srv::builder::Init_AddGesture_Request_name();
}

}  // namespace dex_hand_ros2


namespace dex_hand_ros2
{

namespace srv
{

namespace builder
{

class Init_AddGesture_Response_message
{
public:
  explicit Init_AddGesture_Response_message(::dex_hand_ros2::srv::AddGesture_Response & msg)
  : msg_(msg)
  {}
  ::dex_hand_ros2::srv::AddGesture_Response message(::dex_hand_ros2::srv::AddGesture_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::srv::AddGesture_Response msg_;
};

class Init_AddGesture_Response_success
{
public:
  Init_AddGesture_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_AddGesture_Response_message success(::dex_hand_ros2::srv::AddGesture_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_AddGesture_Response_message(msg_);
  }

private:
  ::dex_hand_ros2::srv::AddGesture_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::srv::AddGesture_Response>()
{
  return dex_hand_ros2::srv::builder::Init_AddGesture_Response_success();
}

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__BUILDER_HPP_
