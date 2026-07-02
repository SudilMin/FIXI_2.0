"""Packaging configuration for fixi_camera."""

from glob import glob

from setuptools import find_packages, setup

package_name = 'fixi_camera'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sudil-minthaka',
    maintainer_email='sudil-minthaka@todo.todo',
    description='USB camera image publisher for the FIXI Bottle robot.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'camera_node = fixi_camera.camera_node:main',
        ],
    },
)
