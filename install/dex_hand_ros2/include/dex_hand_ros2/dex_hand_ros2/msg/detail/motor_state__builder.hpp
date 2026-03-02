// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from dex_hand_ros2:msg/MotorState.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__BUILDER_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "dex_hand_ros2/msg/detail/motor_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace dex_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_MotorState_connected
{
public:
  explicit Init_MotorState_connected(::dex_hand_ros2::msg::MotorState & msg)
  : msg_(msg)
  {}
  ::dex_hand_ros2::msg::MotorState connected(::dex_hand_ros2::msg::MotorState::_connected_type arg)
  {
    msg_.connected = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::msg::MotorState msg_;
};

class Init_MotorState_velocity
{
public:
  explicit Init_MotorState_velocity(::dex_hand_ros2::msg::MotorState & msg)
  : msg_(msg)
  {}
  Init_MotorState_connected velocity(::dex_hand_ros2::msg::MotorState::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_MotorState_connected(msg_);
  }

private:
  ::dex_hand_ros2::msg::MotorState msg_;
};

class Init_MotorState_position
{
public:
  explicit Init_MotorState_position(::dex_hand_ros2::msg::MotorState & msg)
  : msg_(msg)
  {}
  Init_MotorState_velocity position(::dex_hand_ros2::msg::MotorState::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_MotorState_velocity(msg_);
  }

private:
  ::dex_hand_ros2::msg::MotorState msg_;
};

class Init_MotorState_motor_id
{
public:
  Init_MotorState_motor_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorState_position motor_id(::dex_hand_ros2::msg::MotorState::_motor_id_type arg)
  {
    msg_.motor_id = std::move(arg);
    return Init_MotorState_position(msg_);
  }

private:
  ::dex_hand_ros2::msg::MotorState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::msg::MotorState>()
{
  return dex_hand_ros2::msg::builder::Init_MotorState_motor_id();
}

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__BUILDER_HPP_
