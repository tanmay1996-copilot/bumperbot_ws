#include <rclcpp/rclcpp.hpp>
#include <bumperbot_msgs/srv/add_two_ints.hpp>

using namespace std::placeholders;

class SimpleServiceServer : public rclcpp::Node
{
    public:
        SimpleServiceServer() : Node("simple_service_server")
        {
            service_ = this->create_service<bumperbot_msgs::srv::AddTwoInts>(
                "add_two_ints",
                std::bind(&SimpleServiceServer::ServiceCallback, this, _1, _2));

            RCLCPP_INFO_STREAM(get_logger(), "Service server 'add_two_ints' is ready.");
        }

    private:
        rclcpp::Service<bumperbot_msgs::srv::AddTwoInts>::SharedPtr service_;  
        
        void ServiceCallback(std::shared_ptr<bumperbot_msgs::srv::AddTwoInts::Request> req,
                             std::shared_ptr<bumperbot_msgs::srv::AddTwoInts::Response> res)
        {
            RCLCPP_INFO_STREAM(get_logger(), "Received request: a=" << req->a << ", b=" << req->b);
            res->sum = req->a + req->b;
            RCLCPP_INFO_STREAM(get_logger(), "Sending response: sum=" << res->sum);
        }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SimpleServiceServer>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
