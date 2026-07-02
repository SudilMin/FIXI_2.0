# fixi_description

Robot description package for the FIXI Bottle autonomous bottle-collection robot.

The model is written in xacro so dimensions and repeated inertial patterns can
be maintained cleanly as the robot evolves.

## Purpose

- Define the robot's physical link and joint structure.
- Publish a complete TF tree through `robot_state_publisher`.
- Provide an RViz display launch for visual inspection.
- Reserve mesh directories for future CAD/STL assets.

## Main Links

- `base_footprint` - ground-projected root frame.
- `base_link` - main differential-drive chassis.
- `left_wheel_link` and `right_wheel_link` - continuous wheel joints.
- `caster_wheel_link` - passive rear/front support caster.
- `camera_mount_link`, `camera_link`, `camera_optical_frame` - front camera assembly.
- `arm_base_link`, `arm_shoulder_link`, `arm_upper_link`, `arm_forearm_link`, `arm_wrist_link` - 4 DOF arm chain.
- `gripper_base_link`, `left_gripper_finger_link`, `right_gripper_finger_link` - bottle gripper.
- `storage_bin_link` - onboard bottle storage bin.

## Published Topics

When launched:

- `/robot_description` (`std_msgs/msg/String`) from `robot_state_publisher`.
- `/tf` and `/tf_static` from `robot_state_publisher`.
- `/joint_states` from `joint_state_publisher_gui`.

## Subscribed Topics

- `/joint_states` is consumed by `robot_state_publisher`.

## Services

None.

## Parameters

The launch file exposes:

- `model` - path to the xacro file.
- `rviz_config` - path to the RViz config file.
- `use_sim_time` - whether to use simulation time.

## Run

```bash
colcon build --packages-select fixi_description
source install/setup.bash
ros2 launch fixi_description display.launch.py
```

## File Guide

- `package.xml` declares package metadata and runtime dependencies.
- `CMakeLists.txt` installs `launch/`, `urdf/`, `rviz/`, and `meshes/`.
- `launch/display.launch.py` starts `robot_state_publisher`, `joint_state_publisher_gui`, and RViz.
- `urdf/fixi.urdf.xacro` defines the robot links, joints, visuals, collisions, inertials, and TF tree.
- `rviz/fixi.rviz` configures RViz to show the robot model, grid, and TF frames.
- `meshes/` contains placeholder folders for future base, wheel, arm, sensor, and storage-bin mesh files.
