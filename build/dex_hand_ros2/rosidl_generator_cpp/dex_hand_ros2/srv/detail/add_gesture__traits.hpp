// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from dex_hand_ros2:srv/AddGesture.idl
// generated code does not contain a copyright notice

#ifndef DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__TRAITS_HPP_
#define DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "dex_hand_ros2/srv/detail/add_gesture__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace dex_hand_ros2
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddGesture_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << ", ";
  }

  // member: positions
  {
    if (msg.positions.size() == 0) {
      out << "positions: []";
    } else {
      out << "positions: [";
      size_t pending_items = msg.positions.size();
      for (auto item : msg.positions) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: description
  {
    out << "description: ";
    rosidl_generator_traits::value_to_yaml(msg.description, out);
    out << ", ";
  }

  // member: duration
  {
    out << "duration: ";
    rosidl_generator_traits::value_to_yaml(msg.duration, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AddGesture_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << "\n";
  }

  // member: positions
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.positions.size() == 0) {
      out << "positions: []\n";
    } else {
      out << "positions:\n";
      for (auto item : msg.positions) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: description
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "description: ";
    rosidl_generator_traits::value_to_yaml(msg.description, out);
    out << "\n";
  }

  // member: duration
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "duration: ";
    rosidl_generator_traits::value_to_yaml(msg.duration, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddGesture_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace dex_hand_ros2

namespace rosidl_generator_traits
{

[[deprecated("use dex_hand_ros2::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const dex_hand_ros2::srv::AddGesture_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  dex_hand_ros2::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use dex_hand_ros2::srv::to_yaml() instead")]]
inline std::string to_yaml(const dex_hand_ros2::srv::AddGesture_Request & msg)
{
  return dex_hand_ros2::srv::to_yaml(msg);
}

template<>
inline const char * data_type<dex_hand_ros2::srv::AddGesture_Request>()
{
  return "dex_hand_ros2::srv::AddGesture_Request";
}

template<>
inline const char * name<dex_hand_ros2::srv::AddGesture_Request>()
{
  return "dex_hand_ros2/srv/AddGesture_Request";
}

template<>
struct has_fixed_size<dex_hand_ros2::srv::AddGesture_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<dex_hand_ros2::srv::AddGesture_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<dex_hand_ros2::srv::AddGesture_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace dex_hand_ros2
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddGesture_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AddGesture_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddGesture_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace dex_hand_ros2

namespace rosidl_generator_traits
{

[[deprecated("use dex_hand_ros2::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const dex_hand_ros2::srv::AddGesture_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  dex_hand_ros2::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use dex_hand_ros2::srv::to_yaml() instead")]]
inline std::string to_yaml(const dex_hand_ros2::srv::AddGesture_Response & msg)
{
  return dex_hand_ros2::srv::to_yaml(msg);
}

template<>
inline const char * data_type<dex_hand_ros2::srv::AddGesture_Response>()
{
  return "dex_hand_ros2::srv::AddGesture_Response";
}

template<>
inline const char * name<dex_hand_ros2::srv::AddGesture_Response>()
{
  return "dex_hand_ros2/srv/AddGesture_Response";
}

template<>
struct has_fixed_size<dex_hand_ros2::srv::AddGesture_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<dex_hand_ros2::srv::AddGesture_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<dex_hand_ros2::srv::AddGesture_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<dex_hand_ros2::srv::AddGesture>()
{
  return "dex_hand_ros2::srv::AddGesture";
}

template<>
inline const char * name<dex_hand_ros2::srv::AddGesture>()
{
  return "dex_hand_ros2/srv/AddGesture";
}

template<>
struct has_fixed_size<dex_hand_ros2::srv::AddGesture>
  : std::integral_constant<
    bool,
    has_fixed_size<dex_hand_ros2::srv::AddGesture_Request>::value &&
    has_fixed_size<dex_hand_ros2::srv::AddGesture_Response>::value
  >
{
};

template<>
struct has_bounded_size<dex_hand_ros2::srv::AddGesture>
  : std::integral_constant<
    bool,
    has_bounded_size<dex_hand_ros2::srv::AddGesture_Request>::value &&
    has_bounded_size<dex_hand_ros2::srv::AddGesture_Response>::value
  >
{
};

template<>
struct is_service<dex_hand_ros2::srv::AddGesture>
  : std::true_type
{
};

template<>
struct is_service_request<dex_hand_ros2::srv::AddGesture_Request>
  : std::true_type
{
};

template<>
struct is_service_response<dex_hand_ros2::srv::AddGesture_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // DEX_HAND_ROS2__SRV__DETAIL__ADD_GESTURE__TRAITS_HPP_
