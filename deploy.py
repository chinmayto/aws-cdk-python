#!/usr/bin/env python3
"""
Deployment script for AWS CDK Website Stack
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting AWS CDK Website Deployment")
    
    # Check if CDK is installed
    if not run_command("cdk --version", "Checking CDK installation"):
        print("Please install AWS CDK: npm install -g aws-cdk")
        sys.exit(1)
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    # Bootstrap CDK (if not already done)
    print("\n📦 Bootstrapping CDK (this may take a few minutes on first run)...")
    run_command("cdk bootstrap", "CDK Bootstrap")
    
    # Synthesize the stack
    if not run_command("cdk synth", "Synthesizing CDK stack"):
        sys.exit(1)
    
    # Deploy the stack
    if not run_command("cdk deploy --require-approval never", "Deploying stack to AWS"):
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Check the CloudFormation outputs for the Load Balancer DNS name")
    print("2. Wait a few minutes for the instances to be healthy")
    print("3. Access your website using the Load Balancer DNS name")
    print("4. Use the bastion host to SSH into private instances if needed")

if __name__ == "__main__":
    main()