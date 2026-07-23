// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from dex_hand_ros2:msg/PIDconfig.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__BUILDER_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "dex_hand_ros2/msg/detail/pi_dconfig__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace dex_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_PIDconfig_kd
{
public:
  explicit Init_PIDconfig_kd(::dex_hand_ros2::msg::PIDconfig & msg)
  : msg_(msg)
  {}
  ::dex_hand_ros2::msg::PIDconfig kd(::dex_hand_ros2::msg::PIDconfig::_kd_type arg)
  {
    msg_.kd = std::move(arg);
    return std::move(msg_);
  }

private:
  ::dex_hand_ros2::msg::PIDconfig msg_;
};

class Init_PIDconfig_ki
{
public:
  explicit Init_PIDconfig_ki(::dex_hand_ros2::msg::PIDconfig & msg)
  : msg_(msg)
  {}
  Init_PIDconfig_kd ki(::dex_hand_ros2::msg::PIDconfig::_ki_type arg)
  {
    msg_.ki = std::move(arg);
    return Init_PIDconfig_kd(msg_);
  }

private:
  ::dex_hand_ros2::msg::PIDconfig msg_;
};

class Init_PIDconfig_kp
{
public:
  explicit Init_PIDconfig_kp(::dex_hand_ros2::msg::PIDconfig & msg)
  : msg_(msg)
  {}
  Init_PIDconfig_ki kp(::dex_hand_ros2::msg::PIDconfig::_kp_type arg)
  {
    msg_.kp = std::move(arg);
    return Init_PIDconfig_ki(msg_);
  }

private:
  ::dex_hand_ros2::msg::PIDconfig msg_;
};

class Init_PIDconfig_motor_id
{
public:
  Init_PIDconfig_motor_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PIDconfig_kp motor_id(::dex_hand_ros2::msg::PIDconfig::_motor_id_type arg)
  {
    msg_.motor_id = std::move(arg);
    return Init_PIDconfig_kp(msg_);
  }

private:
  ::dex_hand_ros2::msg::PIDconfig msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::dex_hand_ros2::msg::PIDconfig>()
{
  return dex_hand_ros2::msg::builder::Init_PIDconfig_motor_id();
}

}  // namespace dex_hand_ros2

#endif  // DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__BUILDER_HPP_
