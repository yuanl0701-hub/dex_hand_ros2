// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from dex_hand_ros2:srv/ChangeId.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__CHANGE_ID__BUILDER_HPP_
#define DEX_HAND_ROS2__SRV__DETAIL__CHANGE_ID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "dex_hand_ros2/srv/detail/change_id__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace dex_hand_ros2
{

namespace srv
{

namespace builder
{

class Init_ChangeId_Request_command
{
public:
  Init_ChangeId_Request_command()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::dex_hand_ros2::srv::ChangeId_Request command(::dex_hand_ros2::srv::ChangeId_Request::_command_type arg)
  {
    msg_.command = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::srv::ChangeId_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::srv::ChangeId_Request>()
{
  return dex_hand_ros2::srv::builder::Init_ChangeId_Request_command();
}

}  // namespace dex_hand_ros2


namespace dex_hand_ros2
{

namespace srv
{

namespace builder
{

class Init_ChangeId_Response_message
{
public:
  explicit Init_ChangeId_Response_message(::dex_hand_ros2::srv::ChangeId_Response & msg)
  : msg_(msg)
  {}
  ::dex_hand_ros2::srv::ChangeId_Response message(::dex_hand_ros2::srv::ChangeId_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::srv::ChangeId_Response msg_;
};

class Init_ChangeId_Response_success
{
public:
  Init_ChangeId_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ChangeId_Response_message success(::dex_hand_ros2::srv::ChangeId_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_ChangeId_Response_message(msg_);
  }

private:
  ::dex_hand_ros2::srv::ChangeId_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::srv::ChangeId_Response>()
{
  return dex_hand_ros2::srv::builder::Init_ChangeId_Response_success();
}

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__SRV__DETAIL__CHANGE_ID__BUILDER_HPP_
