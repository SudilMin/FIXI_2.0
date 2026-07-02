"""Launch the FIXI Bottle USB camera node."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Create the launch description for the camera publisher."""
    config_file = PathJoinSubstitution(
        [FindPackageShare('fixi_camera'), 'config', 'camera.yaml']
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'config_file',
                default_value=config_file,
                description='Path to the camera node parameter file.',
            ),
            DeclareLaunchArgument('camera_index', default_value='0'),
            DeclareLaunchArgument('frame_width', default_value='640'),
            DeclareLaunchArgument('frame_height', default_value='480'),
            DeclareLaunchArgument('fps', default_value='30.0'),
            DeclareLaunchArgument('frame_id', default_value='camera_link'),
            DeclareLaunchArgument(
                'image_topic',
                default_value='/camera/image_raw',
            ),
            DeclareLaunchArgument('backend', default_value='default'),
            Node(
                package='fixi_camera',
                executable='camera_node',
                name='camera_node',
                output='screen',
                parameters=[
                    LaunchConfiguration('config_file'),
                    {
                        'camera_index': ParameterValue(
                            LaunchConfiguration('camera_index'),
                            value_type=int,
                        ),
                        'frame_width': ParameterValue(
                            LaunchConfiguration('frame_width'),
                            value_type=int,
                        ),
                        'frame_height': ParameterValue(
                            LaunchConfiguration('frame_height'),
                            value_type=int,
                        ),
                        'fps': ParameterValue(
                            LaunchConfiguration('fps'),
                            value_type=float,
                        ),
                        'frame_id': LaunchConfiguration('frame_id'),
                        'image_topic': LaunchConfiguration('image_topic'),
                        'backend': LaunchConfiguration('backend'),
                    },
                ],
            ),
        ]
    )
