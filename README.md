# Building a Highly Available Web Application on AWS with CDK and Python

## Introduction

Infrastructure as Code (IaC) has revolutionized how we provision and manage cloud resources. In this tutorial, we'll explore AWS Cloud Development Kit (CDK) and build a production-ready web application infrastructure with high availability built in.

## What is AWS CDK?

AWS Cloud Development Kit (CDK) is an open-source software development framework that lets you define cloud infrastructure using familiar programming languages like Python, TypeScript, Java, and C#. Instead of writing verbose JSON or YAML templates, you can use the full power of programming languages to define your infrastructure.

### Why Use AWS CDK?

- **Use familiar programming languages**: Write infrastructure code in Python, TypeScript, or other supported languages
- **Leverage IDE features**: Get autocomplete, type checking, and inline documentation
- **Reusable components**: Create and share infrastructure patterns as libraries
- **Higher-level abstractions**: CDK constructs provide sensible defaults and best practices
- **Faster development**: Write less code compared to raw CloudFormation templates

### CDK and CloudFormation: The Perfect Partnership

AWS CDK doesn't replace CloudFormation—it enhances it. Here's how they work together:

1. **You write CDK code** in your preferred programming language (Python in our case)
2. **CDK synthesizes CloudFormation templates** from your code using `cdk synth`
3. **CloudFormation deploys the infrastructure** to AWS
4. **CloudFormation manages the stack lifecycle** (updates, rollbacks, deletions)

This means you get the power of programming languages for authoring and the reliability of CloudFormation for deployment. CDK handles the complexity of generating correct CloudFormation templates, while CloudFormation ensures safe, predictable infrastructure changes.

## Architecture Overview

We'll build a highly available web application with the following architecture:

```
┌─────────────────────────────────────────────────────────────────────┐
│                            Internet                                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Internet Gateway     │
                    └────────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────┐
│                                │                  VPC               │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │          Application Load Balancer (ALB)                    │    │
│  │                  (Public Subnets)                           │    │
│  └──────────────────────┬──────────────────┬───────────────────┘    │
│                         │                  │                        │
│  ┌──────────────────────┼──────────────────┼─────────────────────┐  │
│  │  Availability Zone 1 │                  │ Availability Zone 2 │  │
│  │                      │                  │                     │  │
│  │  ┌───────────────────▼────────────┐  ┌──▼──────────────────┐  │  │
│  │  │   Public Subnet (AZ-1)         │  │ Public Subnet (AZ-2)│  │  │
│  │  │                                │  │                     │  │  │
│  │  │  ┌──────────────────┐          │  │                     │  │  │
│  │  │  │  NAT Gateway     │          │  │                     │  │  │
│  │  │  └────────┬─────────┘          │  │                     │  │  │
│  │  └───────────┼────────────────────┘  └─────────────────────┘  │  │
│  │              │                                                │  │
│  │  ┌───────────▼────────────────┐  ┌────────────────────────┐   │  │
│  │  │   Private Subnet (AZ-1)    │  │  Private Subnet (AZ-2) │   │  │
│  │  │                            │  │                        │   │  │
│  │  │  ┌──────────────────┐      │  │  ┌──────────────────┐  │   │  │
│  │  │  │  EC2 Instance 1  │      │  │  │  EC2 Instance 2  │  │   │  │
│  │  │  │                  │      │  │  │                  │  │   │  │
│  │  │  │                  │      │  │  │                  │  │   │  │
│  │  │  └──────────────────┘      │  │  └──────────────────┘  │   │  │
│  │  │                            │  │                        │   │  │
│  │  └────────────────────────────┘  └────────────────────────┘   │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

```

## Prerequisites

Before we begin, ensure you have:

- **Node.js** (v14 or later) for CDK CLI
- **Python 3.8+** installed

## Project Structure

```
aws-cdk-python/
│
├── app.py                    # CDK app entry point - initializes the stack
├── website_stack.py          # Main infrastructure stack definition
├── deploy.py                 # Deployment helper script
│
├── cdk.json                  # CDK configuration file
├── cdk.context.json          # CDK context values (auto-generated)
│
├── requirements.txt          # Python dependencies
├── setup.py                  # Python package setup file
│
└── cdk.out/                 # CDK synthesized CloudFormation templates (auto-generated)
    ├── WebsiteStack.template.json
    ├── manifest.json
    └── tree.json
```

## Step 1: Install AWS CDK CLI

Install the CDK CLI globally using npm:

```bash
npm install -g aws-cdk
```

Verify the installation:

```bash
cdk --version
```

## Step 2: Set Up the Project

Clone the repository or create a new directory:

```bash
git clone https://github.com/chinmayto/aws-cdk-python.git
cd aws-cdk-python
```

Create a Python virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Step 3: Bootstrap Your AWS Environment

CDK requires a one-time bootstrap process to create resources it needs for deployment (S3 bucket for assets, IAM roles, etc.):

```bash
cdk bootstrap
```

This command creates a CloudFormation stack called `CDKToolkit` in your AWS account.
```bash
>cdk bootstrap
Deploying to account: 197317184204, region: us-east-1
 ⏳  Bootstrapping environment aws://197317184204/us-east-1...
Trusted accounts for deployment: (none)
Trusted accounts for lookup: (none)
Using default execution policy of 'arn:aws:iam::aws:policy/AdministratorAccess'. Pass '--cloudformation-execution-policies' to customize.
CDKToolkit: creating CloudFormation changeset...
CDKToolkit |  0/12 | 10:53:19 pm | REVIEW_IN_PROGRESS   | AWS::CloudFormation::Stack | CDKToolkit User Initiated
.
.
.
CDKToolkit | 12/12 | 10:54:11 pm | CREATE_COMPLETE      | AWS::CloudFormation::Stack | CDKToolkit 
 ✅  Environment aws://197317184204/us-east-1 bootstrapped.
 ```

![alt text](/images/CDKToolkit_stack.png)

## Step 4: Review the Infrastructure Code

Our infrastructure is defined in `website_stack.py`. Let's break down the key components:

### Creating the VPC

The VPC is configured with 2 Availability Zones, public subnets for the load balancer, and private subnets for EC2 instances:

```python
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
```

### Security Groups

We create two security groups: one for the ALB (allowing internet traffic) and one for EC2 instances (allowing traffic only from the ALB):

```python
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
```

### IAM Role for EC2

The IAM role allows EC2 instances to be managed via AWS Systems Manager:

```python
# IAM role for EC2 instances
ec2_role = iam.Role(
    self, "EC2Role",
    assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
    ]
)
```

### User Data Script

The user data script installs Apache and creates a dynamic webpage:

```python
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
```

### Creating EC2 Instances

We create 2 EC2 instances distributed across different Availability Zones:

```python
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
```

### Application Load Balancer

Finally, we create the ALB with a target group and listener:

```python
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
```

### CloudFormation Outputs

We define outputs to easily access important resource information:

```python
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
```

## Step 5: Deploy the Infrastructure

Preview the CloudFormation template that CDK will generate:

```bash
cdk synth
```

Deploy the stack to AWS:

```bash
cdk deploy
```

CDK will show you the changes and ask for confirmation. Type `y` to proceed.

The deployment takes approximately 5-10 minutes. Once complete, you'll see outputs including:

```
>cdk deploy
Deploying to account: 197317184204, region: us-east-1

✨  Synthesis time: 16.13s

WebsiteStack: start: Building WebsiteStack/Custom::VpcRestrictDefaultSGCustomResourceProvider Code
WebsiteStack: success: Built WebsiteStack/Custom::VpcRestrictDefaultSGCustomResourceProvider Code
WebsiteStack: start: Building WebsiteStack Template
WebsiteStack: success: Built WebsiteStack Template
WebsiteStack: start: Publishing WebsiteStack/Custom::VpcRestrictDefaultSGCustomResourceProvider Code (197317184204-us-east-1-78ffe0b8)
WebsiteStack: start: Publishing WebsiteStack Template (197317184204-us-east-1-2ed930b7)
WebsiteStack: success: Published WebsiteStack Template (197317184204-us-east-1-2ed930b7)
WebsiteStack: success: Published WebsiteStack/Custom::VpcRestrictDefaultSGCustomResourceProvider Code (197317184204-us-east-1-78ffe0b8)
Stack WebsiteStack
IAM Statement Changes
┌───┬─────────────────────────────────────────────────┬────────┬─────────────────────────────────────────────────┬─────────────────────────────────────────────────┬───────────┐
│   │ Resource                                        │ Effect │ Action                                          │ Principal                                       │ Condition │
├───┼─────────────────────────────────────────────────┼────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────┼───────────┤ 
│ + │ ${Custom::VpcRestrictDefaultSGCustomResourcePro │ Allow  │ sts:AssumeRole                                  │ Service:lambda.amazonaws.com                    │           │ 
│   │ vider/Role.Arn}                                 │        │                                                 │                                                 │           │ 
├───┼─────────────────────────────────────────────────┼────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────┼───────────┤ 
│ + │ ${EC2Role.Arn}                                  │ Allow  │ sts:AssumeRole                                  │ Service:ec2.amazonaws.com                       │           │ 
├───┼─────────────────────────────────────────────────┼────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────┼───────────┤
│ + │ arn:aws:ec2:us-east-1:197317184204:security-gro │ Allow  │ ec2:AuthorizeSecurityGroupEgress                │ AWS:${Custom::VpcRestrictDefaultSGCustomResourc │           │ 
│   │ up/${WebsiteVPC.DefaultSecurityGroup}           │        │ ec2:AuthorizeSecurityGroupIngress               │ eProvider/Role}                                 │           │ 
│   │                                                 │        │ ec2:RevokeSecurityGroupEgress                   │                                                 │           │ 
│   │                                                 │        │ ec2:RevokeSecurityGroupIngress                  │                                                 │           │ 
└───┴─────────────────────────────────────────────────┴────────┴─────────────────────────────────────────────────┴─────────────────────────────────────────────────┴───────────┘ 
IAM Policy Changes
┌───┬────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│   │ Resource                                                   │ Managed Policy ARN                                                                           │
├───┼────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ + │ ${Custom::VpcRestrictDefaultSGCustomResourceProvider/Role} │ {"Fn::Sub":"arn:${AWS::Partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"} │
├───┼────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ + │ ${EC2Role}                                                 │ arn:${AWS::Partition}:iam::aws:policy/AmazonSSMManagedInstanceCore                           │
└───┴────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘
Security Group Changes
┌───┬─────────────────────────────┬─────┬────────────┬─────────────────────────────┐
│   │ Group                       │ Dir │ Protocol   │ Peer                        │
├───┼─────────────────────────────┼─────┼────────────┼─────────────────────────────┤
│ + │ ${ALBSecurityGroup.GroupId} │ In  │ TCP 80     │ Everyone (IPv4)             │
│ + │ ${ALBSecurityGroup.GroupId} │ In  │ TCP 443    │ Everyone (IPv4)             │
│ + │ ${ALBSecurityGroup.GroupId} │ Out │ Everything │ Everyone (IPv4)             │
├───┼─────────────────────────────┼─────┼────────────┼─────────────────────────────┤
│ + │ ${EC2SecurityGroup.GroupId} │ In  │ TCP 22     │ ${WebsiteVPC.CidrBlock}     │
│ + │ ${EC2SecurityGroup.GroupId} │ In  │ TCP 80     │ ${ALBSecurityGroup.GroupId} │
│ + │ ${EC2SecurityGroup.GroupId} │ Out │ Everything │ Everyone (IPv4)             │
└───┴─────────────────────────────┴─────┴────────────┴─────────────────────────────┘
(NOTE: There may be security-related changes not in this list. See https://github.com/aws/aws-cdk/issues/1299)


"--require-approval" is enabled and stack includes security-sensitive updates: 'Do you wish to deploy these changes' (y/n) y
WebsiteStack: deploying... [1/1]
WebsiteStack: creating CloudFormation changeset...
WebsiteStack |  0/39 | 10:58:15 pm | REVIEW_IN_PROGRESS   | AWS::CloudFormation::Stack                | WebsiteStack User Initiated
.
.
.
WebsiteStack | 39/39 | 11:01:35 pm | CREATE_COMPLETE      | AWS::CloudFormation::Stack                | WebsiteStack

 ✅  WebsiteStack

✨  Deployment time: 213.18s

Outputs:
WebsiteStack.Instance1Id = i-089c31f66c61482a3
WebsiteStack.Instance2Id = i-0af48aefd5e4efcc2
WebsiteStack.LoadBalancerDNS = Websit-Websi-5kyWZuGmscD3-1445557942.us-east-1.elb.amazonaws.com
WebsiteStack.VPCId = vpc-002b8b79c7f0e2f49
Stack ARN:
arn:aws:cloudformation:us-east-1:197317184204:stack/WebsiteStack/33bc7c70-11a6-11f1-8888-0affc0f3836d

✨  Total time: 229.31s
```

## Step 6: Test Your Application

Copy the LoadBalancerDNS value from the outputs and open it in your browser:

```
Websit-Websi-5kyWZuGmscD3-1445557942.us-east-1.elb.amazonaws.com
```

You should see a webpage displaying EC2 instance metadata. Refresh the page multiple times to see the load balancer distributing traffic between the two instances (notice the Instance ID and Availability Zone changing).

![alt text](/images/ec2_1.png)

![alt text](/images/ec2_2.png)

## Step 7: Explore Your Infrastructure

View the CloudFormation stack in the AWS Console:
1. Navigate to CloudFormation service
2. Find the `WebsiteStack` stack
3. Explore Resources, Events, and Outputs tabs

![alt text](/images/WebsiteStack_stack.png)

![alt text](/images/WebsiteStack_stack_2.png)

## Cleanup

To avoid ongoing charges, destroy the infrastructure when you're done:

```bash
cdk destroy
```

Type `y` to confirm. CDK will delete all resources created by the stack.

```bash
>cdk destroy
Deploying to account: 197317184204, region: us-east-1
Are you sure you want to delete: WebsiteStack (y/n) y
WebsiteStack: destroying... [1/1]
WebsiteStack |   0 | 11:08:57 pm | DELETE_IN_PROGRESS   | AWS::CloudFormation::Stack                | WebsiteStack User Initiated
.
.
.
WebsiteStack |  37 | 11:10:22 pm | DELETE_IN_PROGRESS   | AWS::EC2::VPC                             | WebsiteVPC (WebsiteVPCD8B49DC8)

 ✅  WebsiteStack: destroyed
```


## Conclusion

AWS CDK transforms infrastructure provisioning from a tedious, error-prone process into an enjoyable development experience. By leveraging Python and CloudFormation together, we've built a production-ready, highly available web application infrastructure with just a few hundred lines of code.

The combination of CDK's developer-friendly abstractions and CloudFormation's robust deployment engine gives you the best of both worlds: rapid development and reliable operations.

## References

- **GitHub Repository**: [aws-cdk-python](https://github.com/chinmayto/aws-cdk-python)
- **AWS CDK Documentation**: https://docs.aws.amazon.com/cdk/
