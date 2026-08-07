from setuptools import find_packages, setup

setup(
    name="dex_hand_ros2",
    version="0.2.0",
    packages=find_packages(exclude=("test",)),
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Yuan Lei",
    maintainer_email="u3650775@connect.hku.hk",
    description="Layered ROS 2 control and hardware adapters for configurable dexterous hands",
    license="MIT",
)
