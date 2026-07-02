"""Launch FIXI Bottle robot description in RViz."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
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
