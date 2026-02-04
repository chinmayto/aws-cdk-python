#!/usr/bin/env python3
"""
Setup script for AWS CDK Website project
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
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🛠️  Setting up AWS CDK Website Project")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Create virtual environment
    if not os.path.exists(".venv"):
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate && pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        activate_cmd = "source .venv/bin/activate && pip install -r requirements.txt"
    
    if not run_command(activate_cmd, "Installing dependencies in virtual environment"):
        sys.exit(1)
    
    # Check AWS CLI configuration
    print("\n🔍 Checking AWS configuration...")
    if not run_command("aws sts get-caller-identity", "Verifying AWS credentials"):
        print("⚠️  AWS credentials not configured. Please run 'aws configure' first.")
        print("You need:")
        print("- AWS Access Key ID")
        print("- AWS Secret Access Key")
        print("- Default region (e.g., us-east-1)")
        return False
    
    # Check if CDK is installed
    if not run_command("cdk --version", "Checking CDK installation"):
        print("📦 Installing AWS CDK...")
        if not run_command("npm install -g aws-cdk", "Installing CDK globally"):
            print("Please install Node.js and npm first, then run: npm install -g aws-cdk")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Run the deployment: python deploy.py")
    print("3. Or deploy manually: cdk deploy")

if __name__ == "__main__":
    main()