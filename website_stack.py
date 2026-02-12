from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_iam as iam,
    CfnOutput,
    Duration
)
from constructs import Construct

class WebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with public and private subnets
        vpc = ec2.Vpc(
            self, "WebsiteVPC",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # Security group for ALB (public-facing)
        alb_security_group = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True
        )
        
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from internet"
        )
        
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS traffic from internet"
        )

        # Security group for EC2 instances (private)
        ec2_security_group = ec2.SecurityGroup(
            self, "EC2SecurityGroup",
            vpc=vpc,
            description="Security group for EC2 instances",
            allow_all_outbound=True
        )
        
        ec2_security_group.add_ingress_rule(
            alb_security_group,
            ec2.Port.tcp(80),
            "Allow HTTP traffic from ALB"
        )
        
        ec2_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(22),
            "Allow SSH from VPC"
        )

        # IAM role for EC2 instances
        ec2_role = iam.Role(
            self, "EC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        # User data script to install and configure web server
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install -y httpd",
            "systemctl start httpd",
            "systemctl enable httpd",
            "",
            "# Get instance metadata using IMDSv2",
            'TOKEN=$(curl --request PUT "http://169.254.169.254/latest/api/token" --header "X-aws-ec2-metadata-token-ttl-seconds: 3600")',
            'instanceId=$(curl -s http://169.254.169.254/latest/meta-data/instance-id --header "X-aws-ec2-metadata-token: $TOKEN")',
            'instanceAZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone --header "X-aws-ec2-metadata-token: $TOKEN")',
            'privHostName=$(curl -s http://169.254.169.254/latest/meta-data/local-hostname --header "X-aws-ec2-metadata-token: $TOKEN")',
            'privIPv4=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 --header "X-aws-ec2-metadata-token: $TOKEN")',
            "",
            "# Create HTML page",
            'echo "<font face = \\"Verdana\\" size = \\"5\\">"                               > /var/www/html/index.html',
            'echo "<center><h1>AWS Linux VM Deployed with CDK using Python</h1></center>"  >> /var/www/html/index.html',
            'echo "<center> <b>EC2 Instance Metadata</b> </center>"                        >> /var/www/html/index.html',
            'echo "<center> <b>Instance ID:</b> $instanceId </center>"                     >> /var/www/html/index.html',
            'echo "<center> <b>AWS Availablity Zone:</b> $instanceAZ </center>"            >> /var/www/html/index.html',
            'echo "<center> <b>Private Hostname:</b> $privHostName </center>"              >> /var/www/html/index.html',
            'echo "<center> <b>Private IPv4:</b> $privIPv4 </center>"                      >> /var/www/html/index.html',
            'echo "</font>"                                                                >> /var/www/html/index.html'
        )

        # Create 2 EC2 instances in private subnets across different AZs
        instances = []
        private_subnets = vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS).subnets
        
        for i in range(2):
            instance = ec2.Instance(
                self, f"WebInstance{i+1}",
                vpc=vpc,
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
                machine_image=ec2.MachineImage.latest_amazon_linux2023(),
                security_group=ec2_security_group,
                role=ec2_role,
                user_data=user_data,
                vpc_subnets=ec2.SubnetSelection(
                    subnets=[private_subnets[i % len(private_subnets)]]
                ),
                require_imdsv2=True
            )
            instances.append(instance)

        # Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "WebsiteALB",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # Target group
        target_group = elbv2.ApplicationTargetGroup(
            self, "WebsiteTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[targets.InstanceIdTarget(instance.instance_id) for instance in instances],
            health_check=elbv2.HealthCheck(
                path="/",
                interval=Duration.seconds(30)
            )
        )

        # Listener
        listener = alb.add_listener(
            "WebsiteListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group]
        )

        # Outputs
        CfnOutput(
            self, "LoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="DNS name of the load balancer"
        )
        
        CfnOutput(
            self, "Instance1Id",
            value=instances[0].instance_id,
            description="Instance ID of the first EC2 instance"
        )
        
        CfnOutput(
            self, "Instance2Id",
            value=instances[1].instance_id,
            description="Instance ID of the second EC2 instance"
        )
        
        CfnOutput(
            self, "VPCId",
            value=vpc.vpc_id,
            description="VPC ID"
        )