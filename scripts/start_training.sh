#!/bin/bash
set -euo pipefail

# Parameters
STACK_NAME="mosaicbert-stack"
REGION="us-east-1"
INSTANCE_TYPE="p5.48xlarge"
AMI_ID="ami-1234567890abcdef0"  # replace with appropriate DLAMI or custom AMI
KEY_NAME="your-keypair"         # replace with your key pair

# Retrieve resources from CloudFormation stack
VPC_ID=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`VpcId`].OutputValue' --output text)
SUBNET_ID=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`SubnetId`].OutputValue' --output text)
SG_ID=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroupId`].OutputValue' --output text)
PROFILE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfile`].OutputValue' --output text)

# Create FSx for Lustre
FILESYSTEM_ID=$(aws fsx create-file-system \
  --region "$REGION" \
  --file-system-type LUSTRE \
  --storage-capacity 1200 \
  --lustre-configuration ImportPath=s3://mosaicbert-datasets/ \
  --subnet-ids "$SUBNET_ID" \
  --security-group-ids "$SG_ID" \
  --query 'FileSystem.FileSystemId' --output text)

echo "Waiting for FSx to become available..."
aws fsx wait file-system-available --file-system-id "$FILESYSTEM_ID" --region "$REGION"

# Launch EC2 instance
INSTANCE_ID=$(aws ec2 run-instances \
  --region "$REGION" \
  --image-id "$AMI_ID" \
  --count 1 \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --subnet-id "$SUBNET_ID" \
  --security-group-ids "$SG_ID" \
  --iam-instance-profile Arn="$PROFILE_ARN" \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":200}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=mosaicbert-training}]' \
  --query 'Instances[0].InstanceId' --output text)

echo "Instance $INSTANCE_ID launched"
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region "$REGION")
echo "Connect with: ssh -i <path-to-key> ec2-user@$PUBLIC_IP"

# To terminate:
# aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --region "$REGION"
# aws fsx delete-file-system --file-system-id "$FILESYSTEM_ID" --region "$REGION"
