# AWS CDK Website Deployment

Deploy a simple website on AWS EC2 instances in private subnets with an Application Load Balancer using AWS CDK (Python).

## Architecture

- **VPC**: Custom VPC with public and private subnets
- **EC2 Instances**: Auto Scaling Group (2 instances) in private subnets
- **Load Balancer**: Application Load Balancer in public subnets
- **Bastion Host**: For SSH access to private instances

## Prerequisites

- AWS CLI configured (`aws configure`)
- Node.js (for CDK CLI: `npm install -g aws-cdk`)
- Python 3.8+

## Quick Start

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Deploy
cdk bootstrap  # First time only
cdk deploy
```

## Project Files

- `app.py` - CDK app entry point
- `website_stack.py` - Infrastructure stack
- `deploy.py` - Deployment helper script

## Usage

**Deploy**: `cdk deploy` or `python deploy.py`  
**Destroy**: `cdk destroy`  
**View template**: `cdk synth`

After deployment, access your website using the Load Balancer DNS name from the CloudFormation outputs.

## Infrastructure Details

- **Instance Type**: t3.micro (Free Tier)
- **Auto Scaling**: 1-3 instances, desired 2
- **Subnets**: Public (ALB) and Private (EC2)
- **Security**: Proper security groups and IAM roles
