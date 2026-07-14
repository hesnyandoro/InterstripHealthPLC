terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — create this S3 bucket + DynamoDB lock table manually once,
  # before running `terraform init`, then uncomment:
  # backend "s3" {
  #   bucket         = "ihp-terraform-state"
  #   key            = "eks/terraform.tfstate"
  #   region         = "af-south-1"
  #   dynamodb_table = "ihp-terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}
