variable "aws_region" {
  description = "AWS region — AWS East Africa (af-south-1) per the blueprint, or another region if af-south-1 lacks a service you need"
  type        = string
  default     = "af-south-1"
}

variable "project" {
  description = "Short project name used as a prefix for all resources"
  type        = string
  default     = "ihp"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "azs" {
  description = "Availability zones to spread subnets across"
  type        = list(string)
  default     = ["af-south-1a", "af-south-1b"]
}

variable "eks_cluster_version" {
  type    = string
  default = "1.30"
}

variable "eks_node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "eks_node_desired_size" {
  type    = number
  default = 2
}

variable "eks_node_min_size" {
  type    = number
  default = 1
}

variable "eks_node_max_size" {
  type    = number
  default = 4
}

# One ECR repo per microservice — extend this list as services come online
variable "service_names" {
  description = "Names of the microservices, used to create one ECR repo per service"
  type        = list(string)
  default     = ["gateway", "auth", "analytics", "claimguard", "medsource", "envihealth"]
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "db_username" {
  type    = string
  default = "ihp_admin"
}
