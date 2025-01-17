import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription

from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    Shutdown,
    DeclareLaunchArgument,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory("rj_robocup"), "config", "sim.yaml"
    )
    bringup_dir = Path(get_package_share_directory("rj_robocup"))
    launch_dir = bringup_dir / "launch"

    team_flag = LaunchConfiguration("team_flag", default="-b")
    sim_flag = LaunchConfiguration("sim_flag", default="-sim")
    ref_flag = LaunchConfiguration("ref_flag", default="-noref")
    direction_flag = LaunchConfiguration("direction_flag", default="plus")

    stdout_linebuf_envvar = SetEnvironmentVariable(
        "RCUTILS_CONSOLE_STDOUT_LINE_BUFFERED", "1"
    )

    soccer = Node(
        package="rj_robocup",
        executable="soccer",
        output="screen",
        arguments=[team_flag, sim_flag, ref_flag, "-defend", direction_flag],
        parameters=[config],
        on_exit=Shutdown(),
    )

    config_server = Node(
        package="rj_robocup",
        executable="config_server",
        output="screen",
        arguments=[team_flag, sim_flag, ref_flag, "-defend", direction_flag],
        parameters=[config],
        on_exit=Shutdown(),
    )

    radio = Node(
        package="rj_robocup",
        executable="sim_radio_node",
        output="screen",
        parameters=[config],
        on_exit=Shutdown(),
    )

    control = Node(
        package="rj_robocup",
        executable="control_node",
        output="screen",
        parameters=[config],
        on_exit=Shutdown(),
    )

    planner = Node(
        package="rj_robocup",
        executable="planner_node",
        output="screen",
        parameters=[config],
        on_exit=Shutdown(),
    )

    gameplay = Node(
        package="rj_robocup",
        executable="gameplay_node",
        output="screen",
        parameters=[config],
        emulate_tty=True,
        on_exit=Shutdown(),
    )

    vision_receiver_launch_path = str(launch_dir / "vision_receiver.launch.py")
    vision_receiver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(vision_receiver_launch_path)
    )

    ref_receiver = Node(
        package="rj_robocup",
        executable="internal_referee_node",
        output="screen",
        parameters=[config],
        on_exit=Shutdown(),
    )

    vision_filter_launch_path = str(launch_dir / "vision_filter.launch.py")
    vision_filter = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(vision_filter_launch_path)
    )

    global_param_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(launch_dir / "global_param_server.launch.py"))
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("team_flag", default_value=""),
            DeclareLaunchArgument("sim_flag", default_value=""),
            DeclareLaunchArgument("ref_flag", default_value=""),
            DeclareLaunchArgument("direction_flag", default_value="plus"),
            stdout_linebuf_envvar,
            config_server,
            global_param_server,
            soccer,
            radio,
            control,
            planner,
            vision_receiver,
            vision_filter,
            ref_receiver,
            gameplay,
        ]
    )
