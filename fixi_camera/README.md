# fixi_camera

USB camera publisher for the FIXI Bottle robot.

This package opens a USB camera with OpenCV, converts each frame with
`cv_bridge`, and publishes `sensor_msgs/Image` messages for downstream AI
packages such as `fixi_detector`.

## Purpose

- Own camera capture only.
- Publish raw camera frames.
- Avoid detection, navigation, arm control, and state-machine logic.

## Published Topics

- `/camera/image_raw` (`sensor_msgs/msg/Image`) - raw BGR camera frames.

## Subscribed Topics

None.

## Services

None.

## Parameters

- `camera_index` (`int`, default: `0`) - OpenCV camera index.
- `frame_width` (`int`, default: `640`) - requested capture width in pixels.
- `frame_height` (`int`, default: `480`) - requested capture height in pixels.
- `fps` (`double`, default: `30.0`) - requested publish rate and camera FPS.
- `frame_id` (`string`, default: `camera_link`) - image header frame ID.
- `image_topic` (`string`, default: `/camera/image_raw`) - output topic name.
- `backend` (`string`, default: `default`) - OpenCV backend: `default`, `v4l2`, or `gstreamer`.

## Run

Build and source the workspace:

```bash
colcon build --packages-select fixi_camera
source install/setup.bash
```

Run the node directly:

```bash
ros2 run fixi_camera camera_node
```

Run with the launch file:

```bash
ros2 launch fixi_camera camera.launch.py
```

Override parameters:

```bash
ros2 launch fixi_camera camera.launch.py camera_index:=1
```

## File Guide

- `package.xml` declares ROS 2 package metadata and runtime dependencies.
- `setup.py` installs the Python module, launch file, config file, README, and console entry point.
- `setup.cfg` tells ROS 2 where to install executable scripts.
- `fixi_camera/camera_node.py` contains `CameraNode`, the USB camera publisher.
- `launch/camera.launch.py` starts the camera node with a YAML parameter file.
- `config/camera.yaml` stores default camera parameters.
- `resource/fixi_camera` registers the package with the ament index.
- `fixi_camera/__init__.py` marks the Python package.
