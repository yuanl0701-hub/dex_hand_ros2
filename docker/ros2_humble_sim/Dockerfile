FROM ros:humble-ros-base-jammy

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -o Acquire::Retries=5 update && \
    apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-pip \
    python3-pytest \
    python3-rosdep \
    python3-serial \
    ros-humble-robot-state-publisher \
    ros-humble-rviz2 \
    ros-humble-tf2-tools \
    ros-humble-xacro \
    ros-humble-rosbag2 \
    ros-humble-rosbag2-storage-default-plugins \
    fluxbox \
    mesa-utils \
    novnc \
    websockify \
    x11vnc \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_DISTRO=humble \
    ROS_DOMAIN_ID=77 \
    DISPLAY=:1 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    QT_X11_NO_MITSHM=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY docker/ros2_humble_sim/entrypoint.sh /ros_entrypoint_sim.sh
COPY docker/ros2_humble_sim/start_rviz_novnc.sh /start_rviz_novnc.sh
RUN chmod +x /ros_entrypoint_sim.sh /start_rviz_novnc.sh

ENTRYPOINT ["/ros_entrypoint_sim.sh"]
CMD ["bash"]
