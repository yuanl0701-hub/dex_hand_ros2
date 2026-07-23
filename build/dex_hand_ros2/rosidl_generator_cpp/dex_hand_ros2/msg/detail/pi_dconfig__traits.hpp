// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from dex_hand_ros2:msg/PIDconfig.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__TRAITS_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "dex_hand_ros2/msg/detail/pi_dconfig__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace dex_hand_ros2
{

namespace msg
{

inline void to_flow_style_yaml(
  const PIDconfig & msg,
  std::ostream & out)
{
  out << "{";
  // member: motor_id
  {
    out << "motor_id: ";
    rosidl_generator_traits::value_to_yaml(msg.motor_id, out);
    out << ", ";
  }

  // member: kp
  {
    out << "kp: ";
    rosidl_generator_traits::value_to_yaml(msg.kp, out);
    out << ", ";
  }

  // member: ki
  {
    out << "ki: ";
    rosidl_generator_traits::value_to_yaml(msg.ki, out);
    out << ", ";
  }

  // member: kd
  {
    out << "kd: ";
    rosidl_generator_traits::value_to_yaml(msg.kd, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PIDconfig & msg,
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

  // member: kp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kp: ";
    rosidl_generator_traits::value_to_yaml(msg.kp, out);
    out << "\n";
  }

  // member: ki
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ki: ";
    rosidl_generator_traits::value_to_yaml(msg.ki, out);
    out << "\n";
  }

  // member: kd
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kd: ";
    rosidl_generator_traits::value_to_yaml(msg.kd, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PIDconfig & msg, bool use_flow_style = false)
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
  const dex_hand_ros2::msg::PIDconfig & msg,
  std::ostream & out, size_t indentation = 0)
{
  dex_hand_ros2::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use dex_hand_ros2::msg::to_yaml() instead")]]
inline std::string to_yaml(const dex_hand_ros2::msg::PIDconfig & msg)
{
  return dex_hand_ros2::msg::to_yaml(msg);
}

template<>
inline const char * data_type<dex_hand_ros2::msg::PIDconfig>()
{
  return "dex_hand_ros2::msg::PIDconfig";
}

template<>
inline const char * name<dex_hand_ros2::msg::PIDconfig>()
{
  return "dex_hand_ros2/msg/PIDconfig";
}

template<>
struct has_fixed_size<dex_hand_ros2::msg::PIDconfig>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<dex_hand_ros2::msg::PIDconfig>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<dex_hand_ros2::msg::PIDconfig>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DEX_HAND_ROS2__MSG__DETAIL__PI_DCONFIG__TRAITS_HPP_
