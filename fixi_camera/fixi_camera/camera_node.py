"""USB camera publisher node for FIXI Bottle."""

from __future__ import annotations

from typing import Optional

import cv2

from cv_bridge import CvBridge

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy

from sensor_msgs.msg import Image


class CameraNode(Node):
    """Capture frames from a USB camera and publish them as ROS 2 images."""

    def __init__(self) -> None:
        """Initialize parameters, publisher, OpenCV capture, and timer."""
        super().__init__('camera_node')

        self.declare_parameter('camera_index', 0)
        self.declare_parameter('frame_width', 640)
        self.declare_parameter('frame_height', 480)
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('frame_id', 'camera_link')
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('backend', 'default')

        self._camera_index = (
            self.get_parameter('camera_index')
            .get_parameter_value()
            .integer_value
        )
        self._frame_width = (
            self.get_parameter('frame_width')
            .get_parameter_value()
            .integer_value
        )
        self._frame_height = (
            self.get_parameter('frame_height')
            .get_parameter_value()
            .integer_value
        )
        self._fps = (
            self.get_parameter('fps').get_parameter_value().double_value
        )
        self._frame_id = (
            self.get_parameter('frame_id').get_parameter_value().string_value
        )
        self._image_topic = (
            self.get_parameter('image_topic')
            .get_parameter_value()
            .string_value
        )
        self._backend = (
            self.get_parameter('backend').get_parameter_value().string_value
        )

        self._bridge = CvBridge()
        self._capture: Optional[cv2.VideoCapture] = None

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )
        self._publisher = self.create_publisher(
            Image,
            self._image_topic,
            qos_profile,
        )

        self._open_camera()

        timer_period = 1.0 / max(self._fps, 1.0)
        self._timer = self.create_timer(timer_period, self._publish_frame)

        self.get_logger().info(
            f'Publishing USB camera {self._camera_index} to '
            f'{self._image_topic} at {self._fps:.1f} FPS'
        )

    def destroy_node(self) -> bool:
        """Release the camera before shutting down the ROS node."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            self.get_logger().info('Released USB camera')

        return super().destroy_node()

    def _open_camera(self) -> None:
        """Open the configured USB camera and apply capture settings."""
        backend_id = self._backend_to_opencv_id(self._backend)
        if backend_id is None:
            self._capture = cv2.VideoCapture(self._camera_index)
        else:
            self._capture = cv2.VideoCapture(self._camera_index, backend_id)

        if not self._capture.isOpened():
            self.get_logger().error(
                f'Failed to open USB camera index {self._camera_index}'
            )
            return

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, float(self._frame_width))
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self._frame_height))
        self._capture.set(cv2.CAP_PROP_FPS, float(self._fps))

        self.get_logger().info(
            f'Opened USB camera index {self._camera_index} with requested '
            f'size {self._frame_width}x{self._frame_height}'
        )

    def _publish_frame(self) -> None:
        """Read one camera frame and publish it to the image topic."""
        if self._capture is None or not self._capture.isOpened():
            self.get_logger().warn(
                'Camera is not open; skipping frame',
                throttle_duration_sec=5.0,
            )
            return

        success, frame = self._capture.read()
        if not success or frame is None:
            self.get_logger().warn(
                'Failed to read frame from USB camera',
                throttle_duration_sec=5.0,
            )
            return

        image_msg = self._bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        image_msg.header.stamp = self.get_clock().now().to_msg()
        image_msg.header.frame_id = self._frame_id
        self._publisher.publish(image_msg)

    @staticmethod
    def _backend_to_opencv_id(backend: str) -> Optional[int]:
        """Convert a backend parameter string into an OpenCV backend ID."""
        normalized_backend = backend.strip().lower()
        if normalized_backend in ('', 'default', 'auto'):
            return None
        if normalized_backend == 'v4l2':
            return cv2.CAP_V4L2
        if normalized_backend == 'gstreamer':
            return cv2.CAP_GSTREAMER

        return None


def main(args: Optional[list[str]] = None) -> None:
    """Run the FIXI Bottle camera node."""
    rclpy.init(args=args)
    node = CameraNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Camera node stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
