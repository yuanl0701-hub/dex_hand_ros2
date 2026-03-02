// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from dex_hand_ros2:msg/MotorState.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__TRAITS_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "dex_hand_ros2/msg/detail/motor_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace dex_hand_ros2
{

namespace msg
{

inline void to_flow_style_yaml(
  const MotorState & msg,
  std::ostream & out)
{
  out << "{";
  // member: motor_id
  {
    out << "motor_id: ";
    rosidl_generator_traits::value_to_yaml(msg.motor_id, out);
    out << ", ";
  }

  // member: position
  {
    out << "position: ";
    rosidl_generator_traits::value_to_yaml(msg.position, out);
    out << ", ";
  }

  // member: velocity
  {
    out << "velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.velocity, out);
    out << ", ";
  }

  // member: connected
  {
    out << "connected: ";
    rosidl_generator_traits::value_to_yaml(msg.connected, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MotorState & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: motor_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor_id: ";
    rosidl_generator_traits::value_to_yaml(msg.motor_id, out);
    out << "\n";
  }

  // member: position
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "position: ";
    rosidl_generator_traits::value_to_yaml(msg.position, out);
    out << "\n";
  }

  // member: velocity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.velocity, out);
    out << "\n";
  }

  // member: connected
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "connected: ";
    rosidl_generator_traits::value_to_yaml(msg.connected, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MotorState & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace dex_hand_ros2

namespace rosidl_generator_traits
{

[[deprecated("use dex_hand_ros2::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const dex_hand_ros2::msg::MotorState & msg,
  std::ostream & out, size_t indentation = 0)
{
  dex_hand_ros2::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use dex_hand_ros2::msg::to_yaml() instead")]]
inline std::string to_yaml(const dex_hand_ros2::msg::MotorState & msg)
{
  return dex_hand_ros2::msg::to_yaml(msg);
}

template<>
inline const char * data_type<dex_hand_ros2::msg::MotorState>()
{
  return "dex_hand_ros2::msg::MotorState";
}

template<>
inline const char * name<dex_hand_ros2::msg::MotorState>()
{
  return "dex_hand_ros2/msg/MotorState";
}

template<>
struct has_fixed_size<dex_hand_ros2::msg::MotorState>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<dex_hand_ros2::msg::MotorState>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<dex_hand_ros2::msg::MotorState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DEX_HAND_ROS2__MSG__DETAIL__MOTOR_STATE__TRAITS_HPP_
