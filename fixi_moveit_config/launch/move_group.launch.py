import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def generate_launch_description():
    moveit_config_dir = get_package_share_directory('fixi_moveit_config')
    desc_dir = get_package_share_directory('fixi_description')
    
    urdf = os.path.join(desc_dir, 'urdf', 'fixi.urdf.xacro')
    srdf = os.path.join(moveit_config_dir, 'config', 'fixi_bottle.srdf')
    kinematics_path = os.path.join(moveit_config_dir, 'config', 'kinematics.yaml')
    joint_limits_path = os.path.join(moveit_config_dir, 'config', 'joint_limits.yaml')
    controllers_path = os.path.join(moveit_config_dir, 'config', 'moveit_controllers.yaml')
    
    # Read SRDF
    with open(srdf, 'r') as f:
        semantic_content = f.read()
        
    # Generate URDF via xacro
    robot_description = ParameterValue(Command(['xacro ', urdf]), value_type=str)
        
    kinematics_dict = {'robot_description_kinematics': load_yaml(kinematics_path)}
    joint_limits_dict = {'robot_description_planning': load_yaml(joint_limits_path)}
    controllers_dict = load_yaml(controllers_path)
        
    return LaunchDescription([
        Node(
            package='moveit_ros_move_group',
            executable='move_group',
            output='screen',
            parameters=[
                {'robot_description': robot_description},
                {'robot_description_semantic': semantic_content},
                kinematics_dict,
                joint_limits_dict,
                controllers_dict,
                {'use_sim_time': True}
            ]
        )
    ])
