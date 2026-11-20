from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():
    
    use_python_arg = DeclareLaunchArgument(
        "use_python", default_value="false"
    )
    
    wheel_radius_arg = DeclareLaunchArgument(
        "wheel_radius", default_value="0.033"
    )
    
    wheel_base_arg = DeclareLaunchArgument(
        "wheel_base", default_value="0.17"
    )
    
    use_simple_controller_arg = DeclareLaunchArgument(
        "use_simple_controller", default_value="true"
    )
    
    use_python = LaunchConfiguration("use_python")
    wheel_radius = LaunchConfiguration("wheel_radius")
    wheel_base = LaunchConfiguration("wheel_base")
    use_simple_controller = LaunchConfiguration("use_simple_controller")

    cmd_vel_priority_mux = Node(
        package="bumperbot_controller",
        executable="cmd_vel_priority_mux.py",
        parameters=[{"keyboard_timeout": 0.5}],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    
    wheel_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["bumperbot_controller", "--controller-manager", "/controller_manager"],
        condition = UnlessCondition(use_simple_controller)
        
    )
    
    simple_controller = GroupAction(
        condition = IfCondition(use_simple_controller),
        actions = [
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["simple_velocity_controller", "--controller-manager", "/controller_manager"],
                ),
            
            Node(
                package="bumperbot_controller",
                executable="simple_controller.py",
                parameters=[{"wheel_radius": wheel_radius, "wheel_base": wheel_base}],
                condition=IfCondition(use_python)
                ),
                
            Node(
                package="bumperbot_controller",
                executable="simple_controller",
                parameters=[{"wheel_radius": wheel_radius, "wheel_base": wheel_base}],
                condition=UnlessCondition(use_python)
                )
        ]
    )

    
    
    return LaunchDescription([
        use_python_arg,
        wheel_radius_arg,
        wheel_base_arg,
        use_simple_controller_arg,
        cmd_vel_priority_mux,
        joint_state_broadcaster_spawner,
        wheel_controller_spawner,
        simple_controller,
    ])