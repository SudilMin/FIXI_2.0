from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    workspace_dir = os.path.expanduser('~/Documents/fixi_bottle_ws')
    default_model_path = os.path.join(workspace_dir, 'models/plastic_detector/weights/best.pt')

    model_path_arg = DeclareLaunchArgument(
        'model_path',
        default_value=default_model_path,
        description='Absolute path to the YOLO best.pt weights file'
    )

    detector_node = Node(
        package='fixi_detector',
        executable='detector_node',
        name='detector_node',
        output='screen',
        parameters=[{
            'model_path': LaunchConfiguration('model_path')
        }]
    )

    return LaunchDescription([
        model_path_arg,
        detector_node
    ])
