#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from fixi_interfaces.msg import BottleArray

class VisualServoNode(Node):
    def __init__(self):
        super().__init__('visual_servo_node')
        
        self.subscription = self.create_subscription(
            BottleArray,
            '/fixi/detections',
            self.detection_callback,
            10
        )
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Configuration
        self.image_width = 640.0
        self.image_center_x = self.image_width / 2.0
        
        # Servoing parameters
        self.kp_yaw = 0.003       # Proportional gain for turning
        self.center_tolerance = 40.0 # Pixels off center allowed before turning in place
        self.forward_speed = 0.8  # m/s
        self.stop_area = 100000.0  # Stop moving forward if the bottle bounding box area is larger than this

        self.get_logger().info('Visual Servo Node Started. Waiting for detections...')

    def detection_callback(self, msg):
        twist = Twist()
        
        if not msg.detections:
            # Stop if no bottles detected
            self.cmd_pub.publish(twist)
            return
            
        # Find the largest bottle (proxy for nearest)
        nearest_bottle = max(msg.detections, key=lambda b: b.area)
        
        # Calculate offset from center
        error_x = self.image_center_x - nearest_bottle.center_x
        
        if abs(error_x) > self.center_tolerance:
            # Phase 1: Center the bottle (Turn in place)
            twist.linear.x = 0.0
            # Positive error means bottle is on the left -> turn left (positive angular z)
            twist.angular.z = self.kp_yaw * error_x
            
            # Cap max turning speed
            twist.angular.z = max(min(twist.angular.z, 1.0), -1.0)
            self.get_logger().info(f'Centering... Error: {error_x:.1f}, CmdZ: {twist.angular.z:.2f}')
            
        else:
            # Phase 2: Drive towards the bottle
            if nearest_bottle.area < self.stop_area:
                twist.linear.x = self.forward_speed
                # Minor course corrections while driving
                twist.angular.z = self.kp_yaw * error_x
                self.get_logger().info(f'Driving! Area: {nearest_bottle.area:.0f}')
            else:
                # Stop if close enough
                self.get_logger().info(f'Reached Bottle! (Area: {nearest_bottle.area:.0f})')
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                
        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = VisualServoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Publish zero twist before exiting
        twist = Twist()
        node.cmd_pub.publish(twist)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
