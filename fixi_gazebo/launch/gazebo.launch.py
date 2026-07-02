import os
import random
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration

def generate_launch_description():
    pkg_fixi_gazebo = get_package_share_directory('fixi_gazebo')
    pkg_fixi_description = get_package_share_directory('fixi_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(pkg_fixi_gazebo, 'worlds', 'fixi_world.sdf')
    urdf_file = os.path.join(pkg_fixi_description, 'urdf', 'fixi.urdf.xacro')
    bottle_model_dir = os.path.join(pkg_fixi_gazebo, 'models', 'plastic_bottle')

    # Environment variables for Gazebo to find models and define version
    os.environ['GZ_VERSION'] = 'harmonic'
    os.environ['GZ_SIM_RESOURCE_PATH'] = f"{os.environ.get('GZ_SIM_RESOURCE_PATH', '')}:{os.path.join(pkg_fixi_gazebo, 'models')}"

    # Gazebo sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_file]),
            'use_sim_time': True
        }]
    )

    # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'fixi_bottle',
                   '-z', '0.2'],
        output='screen'
    )

    # Spawn Random Bottles
    spawn_bottles_actions = []
    for i in range(5):
        x = random.uniform(-3.0, 3.0)
        y = random.uniform(-3.0, 3.0)
        spawn_bottle = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-file', os.path.join(bottle_model_dir, 'model.sdf'),
                '-name', f'plastic_bottle_{i}',
                '-x', str(x),
                '-y', str(y),
                '-z', '0.2'
            ],
            output='screen'
        )
        spawn_bottles_actions.append(spawn_bottle)

    # Controllers
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    # diff_drive_controller = Node(
    #     package='controller_manager',
    #     executable='spawner',
    #     arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
    # )

    # ROS-GZ Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        output='screen'
    )

    # Remap diff drive cmd_vel
    remap_diff_drive = Node(
        package='topic_tools',
        executable='relay',
        name='cmd_vel_relay',
        arguments=['/cmd_vel', '/diff_drive_controller/cmd_vel_unstamped']
    )

    ld = LaunchDescription()
    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_robot)
    ld.add_action(joint_state_broadcaster)
    # ld.add_action(diff_drive_controller)
    ld.add_action(bridge)
    # Remap is handled via ros2 run topic_tools relay, but topic_tools is not always installed.
    # Instead we will just launch relay if available or tell user to publish to /diff_drive_controller/cmd_vel_unstamped

    for action in spawn_bottles_actions:
        ld.add_action(action)

    return ld
