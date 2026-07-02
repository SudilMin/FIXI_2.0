#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Twist
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from fixi_interfaces.msg import BottleArray
import time
from rclpy.executors import MultiThreadedExecutor

class PickAndPlaceNode(Node):
    def __init__(self):
        super().__init__('pick_and_place_node')
        
        self.subscription = self.create_subscription(
            BottleArray,
            '/fixi/detections',
            self.detection_callback,
            10
        )
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.arm_action_client = ActionClient(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
        self.gripper_action_client = ActionClient(self, FollowJointTrajectory, '/gripper_controller/follow_joint_trajectory')
        
        self.state = 'WAITING'
        self.stop_area = 100000.0  # Trigger threshold
        
        self.arm_joints = ['arm_joint_1_yaw', 'arm_joint_2_shoulder', 'arm_joint_3_elbow', 'arm_joint_4_wrist']
        self.gripper_joints = ['left_gripper_finger_joint']
        
        self.get_logger().info('Pick and Place Node Started. Waiting for action servers...')
        self.arm_action_client.wait_for_server()
        self.gripper_action_client.wait_for_server()
        self.get_logger().info('Action servers found! Drive the robot towards a bottle.')

    def detection_callback(self, msg):
        if self.state != 'WAITING':
            return
            
        if not msg.detections:
            return
            
        nearest_bottle = max(msg.detections, key=lambda b: b.area)
        
        if nearest_bottle.area > self.stop_area:
            self.get_logger().info(f'Bottle found in range! Area: {nearest_bottle.area:.0f}. Starting pick sequence!')
            self.state = 'WORKING'
            
            # Hit the brakes!
            twist = Twist()
            self.cmd_pub.publish(twist)
            
            # Start the sequence asynchronously
            self.timer = self.create_timer(0.1, self.execute_sequence)
            
    def execute_sequence(self):
        self.timer.cancel()
        
        # 1. Open gripper
        self.get_logger().info('Opening gripper...')
        self.send_gripper_goal(0.035)
        time.sleep(1.0)
        
        # 2. Reach down
        self.get_logger().info('Reaching for bottle...')
        self.send_arm_goal([0.0, 1.2, -1.0, 0.0], 2.0)
        time.sleep(2.5)
        
        # 3. Close gripper
        self.get_logger().info('Grasping bottle...')
        self.send_gripper_goal(0.01) # Close tightly
        time.sleep(1.0)
        
        # 4. Lift up
        self.get_logger().info('Lifting bottle...')
        self.send_arm_goal([0.0, 0.0, 0.0, 0.0], 2.0)
        time.sleep(2.5)
        
        # 5. Rotate to bin
        self.get_logger().info('Rotating 180 degrees to storage bin...')
        # Yaw 3.14 rad (180 deg), shoulder slightly pitched to drop
        self.send_arm_goal([3.14, 0.5, 0.0, 0.0], 2.5)
        time.sleep(3.0)
        
        # 6. Drop bottle
        self.get_logger().info('Dropping bottle into bin...')
        self.send_gripper_goal(0.035)
        time.sleep(1.0)
        
        # 7. Return to rest
        self.get_logger().info('Returning to rest position...')
        self.send_arm_goal([0.0, 0.0, 0.0, 0.0], 2.5)
        time.sleep(3.0)
        
        self.get_logger().info('Sequence complete! Ready for next bottle.')
        self.state = 'WAITING'

    def send_arm_goal(self, positions, duration_sec):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self.arm_joints
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        
        goal_msg.trajectory.points.append(point)
        self.arm_action_client.send_goal_async(goal_msg)

    def send_gripper_goal(self, position):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self.gripper_joints
        
        point = JointTrajectoryPoint()
        point.positions = [position]
        point.time_from_start = Duration(sec=1, nanosec=0)
        
        goal_msg.trajectory.points.append(point)
        self.gripper_action_client.send_goal_async(goal_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlaceNode()
    
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
