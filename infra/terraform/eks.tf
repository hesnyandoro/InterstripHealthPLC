module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project}-${var.environment}"
  cluster_version = var.eks_cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true # lock this down to office/VPN CIDRs once you have one

  eks_managed_node_groups = {
    default = {
      instance_types = var.eks_node_instance_types
      desired_size   = var.eks_node_desired_size
      min_size       = var.eks_node_min_size
      max_size       = var.eks_node_max_size
      capacity_type  = "ON_DEMAND"
    }
  }

  # Lets you `kubectl` in as your current AWS identity right after apply
  enable_cluster_creator_admin_permissions = true
}

# Needed by the AWS Load Balancer Controller (for Ingress) — install via Helm after cluster is up
module "irsa_lb_controller" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.39"

  role_name                              = "${var.project}-${var.environment}-lb-controller"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}
