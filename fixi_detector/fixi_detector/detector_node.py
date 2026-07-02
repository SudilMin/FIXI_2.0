#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2
from ultralytics import YOLO
import os

from fixi_interfaces.msg import BottleArray, BottleDetection

class DetectorNode(Node):
    def __init__(self):
        super().__init__('bottle_detector')
        
        self.declare_parameter('model_path', 'models/plastic_detector/weights/best.pt')
        model_path = self.get_parameter('model_path').get_parameter_value().string_value
        
        model_path = os.path.expanduser(model_path)
        if not os.path.isabs(model_path):
            workspace_dir = os.path.expanduser('~/Documents/fixi_bottle_ws')
            model_path = os.path.join(workspace_dir, model_path)
            
        self.get_logger().info(f'Loading YOLO model from: {model_path}')
        
        try:
            self.model = YOLO(model_path)
            self.get_logger().info('YOLO model loaded successfully!')
        except Exception as e:
            self.get_logger().error(f'Failed to load YOLO model: {e}')
            return
        
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        self.detection_pub = self.create_publisher(BottleArray, '/fixi/detections', 10)
        self.image_pub = self.create_publisher(Image, '/fixi/detection_image', 10)

    def image_callback(self, msg):
        try:
            # Manual conversion from ROS Image to OpenCV to bypass cv_bridge C++ errors
            cv_image = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height, msg.width, 3))
            if msg.encoding == 'rgb8':
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        except Exception as e:
            self.get_logger().error(f'Manual conversion error: {e}')
            return

        # Run inference
        results = self.model(cv_image, verbose=False)
        
        bottle_array_msg = BottleArray()
        bottle_array_msg.header = msg.header
        
        annotated_image = cv_image.copy()

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls_id = int(box.cls[0].item())
                cls_name = self.model.names[cls_id]
                
                if 'bottle' in cls_name.lower() or cls_name == 'plastic_bottle':
                    detection = BottleDetection()
                    detection.header = msg.header
                    detection.class_id = cls_id
                    detection.class_name = cls_name
                    detection.confidence = conf
                    
                    detection.xmin = x1
                    detection.ymin = y1
                    detection.xmax = x2
                    detection.ymax = y2
                    
                    detection.width = x2 - x1
                    detection.height = y2 - y1
                    detection.center_x = x1 + (detection.width / 2.0)
                    detection.center_y = y1 + (detection.height / 2.0)
                    detection.area = detection.width * detection.height
                    
                    bottle_array_msg.detections.append(detection)
                    
                    cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    label = f"{cls_name} {conf:.2f}"
                    cv2.putText(annotated_image, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        self.detection_pub.publish(bottle_array_msg)
        
        # Manual conversion back to ROS Image
        try:
            annotated_msg = Image()
            annotated_msg.header = msg.header
            annotated_msg.height = annotated_image.shape[0]
            annotated_msg.width = annotated_image.shape[1]
            annotated_msg.encoding = 'bgr8'
            annotated_msg.is_bigendian = False
            annotated_msg.step = annotated_image.shape[1] * 3
            annotated_msg.data = annotated_image.tobytes()
            
            self.image_pub.publish(annotated_msg)
        except Exception as e:
            self.get_logger().error(f'Manual Image creation error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
