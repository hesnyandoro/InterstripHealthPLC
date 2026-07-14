module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${var.project}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs             = var.azs
  private_subnets = [for i, az in var.azs : cidrsubnet(var.vpc_cidr, 4, i)]
  public_subnets  = [for i, az in var.azs : cidrsubnet(var.vpc_cidr, 4, i + 8)]

  enable_nat_gateway   = true
  single_nat_gateway   = true # cheaper for dev; set false for prod HA
  enable_dns_hostnames = true

  # Required tags for EKS + the AWS Load Balancer Controller to auto-discover subnets
  public_subnet_tags = {
    "kubernetes.io/role/elb"                             = "1"
    "kubernetes.io/cluster/${var.project}-${var.environment}" = "shared"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"                    = "1"
    "kubernetes.io/cluster/${var.project}-${var.environment}" = "shared"
  }
}
