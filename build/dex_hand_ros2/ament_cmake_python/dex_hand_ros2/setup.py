from setuptools import find_packages
from setuptools import setup

setup(
    name='dex_hand_ros2',
    version='0.1.0',
    packages=find_packages(
        include=('dex_hand_ros2', 'dex_hand_ros2.*')),
)
