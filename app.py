#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import Environment
import boto3
import os
from website_stack import WebsiteStack

app = cdk.App()

# Try to get account and region from various sources
def get_aws_account_id():
    """Get AWS account ID from current credentials"""
    try:
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
    except Exception:
        return None

def get_aws_region():
    """Get AWS region from various sources"""
    # Try environment variable first
    region = os.environ.get('AWS_DEFAULT_REGION') or os.environ.get('AWS_REGION')
    if region:
        return region
    
    # Try boto3 session
    try:
        session = boto3.Session()
        return session.region_name
    except Exception:
        return "us-east-1"  # Default fallback

# Get account and region
account = app.node.try_get_context("account") or get_aws_account_id()
region = app.node.try_get_context("region") or get_aws_region()

if not account:
    print("Warning: Could not determine AWS account ID. Make sure AWS credentials are configured.")
    print("You can also set it manually: cdk deploy --context account=YOUR_ACCOUNT_ID")
    account = "123456789012"  # Fallback

print(f"Deploying to account: {account}, region: {region}")

env = Environment(account=account, region=region)

WebsiteStack(app, "WebsiteStack", env=env)

app.synth()