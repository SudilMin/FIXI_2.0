# fixi_interfaces

Custom ROS 2 messages and services shared by the FIXI Bottle robot packages.

This package owns interface definitions only. It does not run AI, control motors,
move the arm, or implement robot behavior.

## Purpose

- Define bottle detection messages published by `fixi_detector`.
- Define tracked target messages published by `fixi_tracker`.
- Define arm service contracts used by `fixi_arm` and `fixi_state_machine`.

## Published Topics

None.

## Subscribed Topics

None.

## Services

This package defines service types but does not provide service servers.

- `fixi_interfaces/srv/PickBottle`
- `fixi_interfaces/srv/DropBottle`

## Messages

- `fixi_interfaces/msg/BottleDetection`
- `fixi_interfaces/msg/BottleArray`
- `fixi_interfaces/msg/TargetBottle`

## Parameters

None.

## Notes

Build this package before packages that import its generated Python modules:

```bash
colcon build --packages-select fixi_interfaces
source install/setup.bash
```
