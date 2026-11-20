#include "bumperbot_cpp_examples/simple_tf_kinematics.hpp"

using namespace std::chrono_literals;

SimpleTfKinematics::SimpleTfKinematics(const std::string &name)
    : Node(name), last_x_(0.0), x_increment_(0.05)



{
    static_tf_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);

    dynamic_tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

    static_transform_stamped_.header.stamp = get_clock()->now();
    static_transform_stamped_.header.frame_id = "bumperbot_base";
    static_transform_stamped_.child_frame_id = "bumperbot_top";
    static_transform_stamped_.transform.translation.x = 0.0;
    static_transform_stamped_.transform.translation.y = 0.0;
    static_transform_stamped_.transform.translation.z = 0.3;
    static_transform_stamped_.transform.rotation.x = 0.0; // No rotation around x-axis
    static_transform_stamped_.transform.rotation.y = 0.0; // No rotation around y-axis
    static_transform_stamped_.transform.rotation.z = 0.0; // No rotation around z-axis
    static_transform_stamped_.transform.rotation.w = 1.0; // No rotation (identity quaternion)

    static_tf_broadcaster_->sendTransform(static_transform_stamped_);

    RCLCPP_INFO(get_logger(), "Publishing static transform between %s and %s",
                static_transform_stamped_.header.frame_id.c_str(),
                static_transform_stamped_.child_frame_id.c_str());

    timer_ = create_wall_timer(0.1s, std::bind(&SimpleTfKinematics::timerCallback, this));

}

void SimpleTfKinematics::timerCallback()
{
    dynamic_transform_stamped_.header.stamp = get_clock()->now();
    dynamic_transform_stamped_.header.frame_id = "odom";
    dynamic_transform_stamped_.child_frame_id = "bumperbot_base";
    dynamic_transform_stamped_.transform.translation.x = last_x_ + x_increment_;
    dynamic_transform_stamped_.transform.translation.y = 0.0;
    dynamic_transform_stamped_.transform.translation.z = 0.0;

    // Update the orientation incrementally
    //last_orientation_ *= orientation_increment_;
    dynamic_transform_stamped_.transform.rotation.y = 0.0;
    dynamic_transform_stamped_.transform.rotation.x = 0.0;
    dynamic_transform_stamped_.transform.rotation.z = 0.0;
    dynamic_transform_stamped_.transform.rotation.w = 1.0;

    dynamic_tf_broadcaster_->sendTransform(dynamic_transform_stamped_);

    last_x_ = dynamic_transform_stamped_.transform.translation.x;

    RCLCPP_INFO(get_logger(), "Publishing dynamic transform between %s and %s",
                dynamic_transform_stamped_.header.frame_id.c_str(),
                dynamic_transform_stamped_.child_frame_id.c_str());

    // Update the position for the next callback
    //last_x_ += x_increment_;
}

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SimpleTfKinematics>("simple_tf_kinematics");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}