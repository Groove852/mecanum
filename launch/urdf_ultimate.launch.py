import os
import random

import launch
import launch_ros
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory, get_package_prefix

# this is the function launch  system will look for
def generate_launch_description():

    ####### DATA INPUT ##########
    urdf_file = 'mecanum_ultimate_fixed.urdf'

    package_description = "mecanum_base"

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_worlds_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_share = launch_ros.substitutions.FindPackageShare(package='mecanum_base').find('mecanum_base')

    robot_base_name = "mecanum"

    worlds_package_name = "turtlebot3_gazebo"

    install_dir = get_package_prefix(worlds_package_name)

    gazebo_models_path = os.path.join(pkg_worlds_gazebo, 'models')

    position = [0.0, 0.0, 0.5]
    orientation = [-1.57080, 0.0, 0.0]

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    
    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    print("Fetching URDF ==>")
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "urdf", urdf_file)
    entity_name = robot_base_name+"-"+str(int(random.random()*100000))

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )    

    # Spawn ROBOT Set Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=['-entity',
                    entity_name,
                    '-x', str(position[0]), '-y', str(position[1]), '-z', str(position[2]),
                    '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                    '-topic', '/robot_description'
                    ]
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 'robot_description': Command(['xacro ', robot_desc_path])}],
        output="screen"
    )

    robot_localization_node = launch_ros.actions.Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[os.path.join(pkg_share, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'rviz_basec_settings.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir])

    spawn_controller = Node( 
        package="controller_manager", 
        executable="spawner", 
        arguments=["joint_state_broadcaster"], 
        output="screen", 
    ) 

    # create and return launch description object
    return LaunchDescription(
        [            
            DeclareLaunchArgument(name='use_sim_time', default_value='True',
                                                 description='Flag to enable use_sim_time'),
            # DeclareLaunchArgument('world',
            #                        default_value=[os.path.join(pkg_worlds_gazebo, 'worlds', 'empty_world.world'), ''],
            #                        description='SDF world file'),
            gazebo,
            spawn_robot,
            robot_state_publisher_node,
            rviz_node,
            spawn_controller,
            robot_localization_node
        ]
    )