# world list:
#   distribution_center.world  
#   house.world
#   basic.world        
#   hospital_2_floors.world    
#   inventory.world
#   cafe.world         
#   hospital_3_floors.world    
#   lawn.world
#   caffe_world.world  
#   hospital.world             
#   warehouse.world

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable

def generate_launch_description():

    world_file_name = 'cafe.world'
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    package_description = "mecanum_base"
    world = os.path.join(get_package_share_directory('ar_ht_gazebo'), 'worlds', world_file_name)
    launch_file_dir = os.path.join(get_package_share_directory('mecanum_base'), 'launch')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    sdf = os.path.join(get_package_share_directory('mecanum_base'), 'models/mecanum_ultimate', 'model.sdf')

    # RVIZ Configuration
    # rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'rviz_basec_settings.rviz')

    return LaunchDescription([
        
        # DeclareLaunchArgument(name='use_sim_time', default_value='True',
        #                       description='Flag to enable use_sim_time'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={'world': world}.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),

        Node(package='ar_ht_gazebo', 
            executable='spawn_robot.py', 
            arguments=["--robot_sdf", sdf,
            "--robot_name", "ar_ht_mecanum",
            "--robot_namespace", "",
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.5"],
             output='screen'
        ),

        Node(
            package='gazebo_noiser',
            executable='noise_odom',
            name='noise_odom_node',
            output='log',
            parameters=[{
                "alpha_0": 1.0,
                "alpha_1": 1.0,
                "alpha_2": 1.0,
                "alpha_3": 1.0,
                "alpha_4": 1.0,
                "alpha_5": 1.0
            }],
            emulate_tty=True,
        ),

        Node( 
            package="controller_manager", 
            executable="spawner", 
            arguments=["joint_state_broadcaster"], 
            output="screen",
        ),
        
        # Node(
        #     package='rviz2',
        #     executable='rviz2',
        #     output='screen',
        #     name='rviz_node',
        #     parameters=[{'use_sim_time': True}],
        #     arguments=['-d', rviz_config_dir],
        # ),
    ])
