// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from dex_hand_ros2:msg/GestureCmd.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__TRAITS_HPP_
#define DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "dex_hand_ros2/msg/detail/gesture_cmd__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace dex_hand_ros2
{

namespace msg
{

inline void to_flow_style_yaml(
  const GestureCmd & msg,
  std::ostream & out)
{
  out << "{";
  // member: gesture
  {
    out << "gesture: ";
    rosidl_generator_traits::value_to_yaml(msg.gesture, out);
    out << ", ";
  }

  // member: speed
  {
    out << "speed: ";
    rosidl_generator_traits::value_to_yaml(msg.speed, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GestureCmd & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: gesture
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "gesture: ";
    rosidl_generator_traits::value_to_yaml(msg.gesture, out);
    out << "\n";
  }

  // member: speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "speed: ";
    rosidl_generator_traits::value_to_yaml(msg.speed, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GestureCmd & msg, bool use_flow_style = false)
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
  const dex_hand_ros2::msg::GestureCmd & msg,
  std::ostream & out, size_t indentation = 0)
{
  dex_hand_ros2::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use dex_hand_ros2::msg::to_yaml() instead")]]
inline std::string to_yaml(const dex_hand_ros2::msg::GestureCmd & msg)
{
  return dex_hand_ros2::msg::to_yaml(msg);
}

template<>
inline const char * data_type<dex_hand_ros2::msg::GestureCmd>()
{
  return "dex_hand_ros2::msg::GestureCmd";
}

template<>
inline const char * name<dex_hand_ros2::msg::GestureCmd>()
{
  return "dex_hand_ros2/msg/GestureCmd";
}

template<>
struct has_fixed_size<dex_hand_ros2::msg::GestureCmd>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<dex_hand_ros2::msg::GestureCmd>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<dex_hand_ros2::msg::GestureCmd>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DEX_HAND_ROS2__MSG__DETAIL__GESTURE_CMD__TRAITS_HPP_
