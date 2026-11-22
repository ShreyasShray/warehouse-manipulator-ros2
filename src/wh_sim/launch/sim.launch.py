import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_share = get_package_share_directory('wh_description')
    sim_share = get_package_share_directory('wh_sim')
    xacro_file = os.path.join(desc_share, 'urdf', 'base.urdf.xacro')
    world = os.path.join(sim_share, 'worlds', 'warehouse.sdf')
    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    # Lets Gazebo resolve package://wh_description/meshes/...
    res = os.path.dirname(desc_share)
    old = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    set_res = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', res + (':' + old if old else ''))

    gz = ExecuteProcess(cmd=['gz', 'sim', '-r', world], output='screen')

    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_desc, 'use_sim_time': True}])

    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-topic', 'robot_description', '-name', 'wh_base',
                            '-x', '-3.0', '-y', '0.0', '-z', '0.1'],
                 output='screen')

    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  arguments=[
                      '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                      '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                      '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                      '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                      '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
                      '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                      '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
                  ],
                  output='screen')

    return LaunchDescription([set_res, gz, rsp, spawn, bridge])
