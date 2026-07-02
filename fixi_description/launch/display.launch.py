"""Launch FIXI Bottle robot description in RViz."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Create a display launch for robot_state_publisher, JSP GUI, and RViz."""
    description_package = FindPackageShare('fixi_description')
    default_model_path = PathJoinSubstitution(
        [description_package, 'urdf', 'fixi.urdf.xacro']
    )
    default_rviz_path = PathJoinSubstitution(
        [description_package, 'rviz', 'fixi.rviz']
    )

    model = LaunchConfiguration('model')
    rviz_config = LaunchConfiguration('rviz_config')
    use_sim_time = LaunchConfiguration('use_sim_time')
    publish_demo_static_tf = LaunchConfiguration('publish_demo_static_tf')

    robot_description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', model]),
        value_type=str,
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'model',
                default_value=default_model_path,
                description='Absolute path to the FIXI Bottle xacro model.',
            ),
            DeclareLaunchArgument(
                'rviz_config',
                default_value=default_rviz_path,
                description='Absolute path to the RViz configuration file.',
            ),
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='false',
                description='Use simulation clock when true.',
            ),
            DeclareLaunchArgument(
                'publish_demo_static_tf',
                default_value='true',
                description=(
                    'Publish static map->odom and odom->base_footprint '
                    'for RViz/view_frames demos. Disable on the real robot '
                    'when odometry or localization publishes these frames.'
                ),
            ),
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[
                    {
                        'robot_description': robot_description,
                        'use_sim_time': use_sim_time,
                    }
                ],
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='map_to_odom_static_tf',
                arguments=[
                    '--x',
                    '0',
                    '--y',
                    '0',
                    '--z',
                    '0',
                    '--roll',
                    '0',
                    '--pitch',
                    '0',
                    '--yaw',
                    '0',
                    '--frame-id',
                    'map',
                    '--child-frame-id',
                    'odom',
                ],
                condition=IfCondition(publish_demo_static_tf),
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='odom_to_base_footprint_static_tf',
                arguments=[
                    '--x',
                    '0',
                    '--y',
                    '0',
                    '--z',
                    '0',
                    '--roll',
                    '0',
                    '--pitch',
                    '0',
                    '--yaw',
                    '0',
                    '--frame-id',
                    'odom',
                    '--child-frame-id',
                    'base_footprint',
                ],
                condition=IfCondition(publish_demo_static_tf),
            ),
            Node(
                package='joint_state_publisher_gui',
                executable='joint_state_publisher_gui',
                name='joint_state_publisher_gui',
                output='screen',
                parameters=[{'use_sim_time': use_sim_time}],
            ),
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': use_sim_time}],
            ),
        ]
    )
