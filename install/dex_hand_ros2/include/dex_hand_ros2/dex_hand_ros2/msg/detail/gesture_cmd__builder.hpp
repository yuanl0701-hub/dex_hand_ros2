// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from dex_hand_ros2:msg/GestureCmd.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__BUILDER_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "dex_hand_ros2/msg/detail/gesture_cmd__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace dex_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_GestureCmd_speed
{
public:
  explicit Init_GestureCmd_speed(::dex_hand_ros2::msg::GestureCmd & msg)
  : msg_(msg)
  {}
  ::dex_hand_ros2::msg::GestureCmd speed(::dex_hand_ros2::msg::GestureCmd::_speed_type arg)
  {
    msg_.speed = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::msg::GestureCmd msg_;
};

class Init_GestureCmd_gesture
{
public:
  Init_GestureCmd_gesture()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GestureCmd_speed gesture(::dex_hand_ros2::msg::GestureCmd::_gesture_type arg)
  {
    msg_.gesture = std::move(arg);
    return Init_GestureCmd_speed(msg_);
  }

private:
  ::dex_hand_ros2::msg::GestureCmd msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::msg::GestureCmd>()
{
  return dex_hand_ros2::msg::builder::Init_GestureCmd_gesture();
}

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__BUILDER_HPP_
