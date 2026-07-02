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

- `map` - global reference frame. The display launch can publish it as a demo static parent.
- `odom` - local odometry frame. A future odometry or Nav2 node should publish this on the real robot.
- `base_footprint` - ground-projected robot frame with no roll, pitch, or body height.
- `base_link` - main differential-drive chassis frame.
- `left_wheel_link` - left drive wheel frame from `left_wheel_joint`.
- `right_wheel_link` - right drive wheel frame from `right_wheel_joint`.
- `caster_wheel_link` - passive caster support frame.
- `camera_mount_link` - fixed bracket mounted at the front of the chassis.
- `camera_link` - physical USB camera body frame.
- `camera_optical_frame` - ROS optical camera frame for image geometry.
- `front_ultrasonic_link` - front ultrasonic sensor body.
- `front_ultrasonic_frame` - front ultrasonic measurement ray origin.
- `left_ultrasonic_link` - left ultrasonic sensor body.
- `left_ultrasonic_frame` - left ultrasonic measurement ray origin.
- `right_ultrasonic_link` - right ultrasonic sensor body.
- `right_ultrasonic_frame` - right ultrasonic measurement ray origin.
- `rear_ultrasonic_link` - rear ultrasonic sensor body.
- `rear_ultrasonic_frame` - rear ultrasonic measurement ray origin.
- `storage_bin_link` - onboard bottle storage bin.
- `arm_base_link` - fixed base plate of the robotic arm.
- `arm_shoulder_link` - first moving arm link, controlled by yaw joint 1.
- `arm_upper_link` - upper arm link, controlled by shoulder joint 2.
- `arm_forearm_link` - forearm link, controlled by elbow joint 3.
- `arm_wrist_link` - wrist link, controlled by wrist joint 4.
- `gripper_base_link` - fixed palm/base of the gripper.
- `left_gripper_finger_link` - left prismatic gripper finger.
- `right_gripper_finger_link` - right prismatic gripper finger, mimicking the left finger.
- `gripper_tcp` - tool center point between the fingers for pickup planning.

## TF Sources

- `robot_state_publisher` publishes all fixed xacro joints on `/tf_static`.
- `robot_state_publisher` publishes moving joints on `/tf` after receiving `/joint_states`.
- `joint_state_publisher_gui` publishes `/joint_states` for display and manual testing.
- `map -> odom` and `odom -> base_footprint` are optional demo static transforms in `display.launch.py`.
- On the real robot, disable demo static transforms and let odometry/localization publish `odom -> base_footprint` and `map -> odom`.

## Published Topics

When launched:

- `/robot_description` (`std_msgs/msg/String`) from `robot_state_publisher`.
- `/tf` and `/tf_static` from `robot_state_publisher` and optional static transform publishers.
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
- `publish_demo_static_tf` - whether to publish demo `map -> odom -> base_footprint` static transforms.

## Run

```bash
colcon build --packages-select fixi_description
source install/setup.bash
ros2 launch fixi_description display.launch.py
```

For real robot runs where another node publishes odometry:

```bash
ros2 launch fixi_description display.launch.py publish_demo_static_tf:=false
```

Generate a TF diagram:

```bash
ros2 run tf2_tools view_frames
```

`view_frames` writes a frame graph PDF in the current directory.

## File Guide

- `package.xml` declares package metadata and runtime dependencies.
- `CMakeLists.txt` installs `launch/`, `urdf/`, `rviz/`, and `meshes/`.
- `launch/display.launch.py` starts `robot_state_publisher`, `joint_state_publisher_gui`, and RViz.
- `urdf/fixi.urdf.xacro` defines the robot links, joints, visuals, collisions, inertials, and TF tree.
- `rviz/fixi.rviz` configures RViz to show the robot model, grid, and TF frames.
- `meshes/` contains placeholder folders for future base, wheel, arm, sensor, and storage-bin mesh files.
