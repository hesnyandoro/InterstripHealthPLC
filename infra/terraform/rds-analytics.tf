# Each microservice owns its own database — this is the Analytics service's.
# Copy/adapt this file per service (rds-claimguard.tf, rds-medsource.tf, ...) as they come online,
# rather than sharing one instance across services.

resource "aws_db_subnet_group" "analytics" {
  name       = "${var.project}-${var.environment}-analytics-db"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "analytics_db" {
  name   = "${var.project}-${var.environment}-analytics-db-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    description     = "Postgres from EKS nodes only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "random_password" "analytics_db" {
  length  = 24
  special = false
}

resource "aws_secretsmanager_secret" "analytics_db" {
  name = "${var.project}-${var.environment}-analytics-db-credentials"
}

resource "aws_secretsmanager_secret_version" "analytics_db" {
  secret_id = aws_secretsmanager_secret.analytics_db.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.analytics_db.result
    host     = aws_db_instance.analytics.address
    port     = 5432
    dbname   = "ihp_analytics"
  })
}

resource "aws_db_instance" "analytics" {
  identifier             = "${var.project}-${var.environment}-analytics"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  db_name                = "ihp_analytics"
  username               = var.db_username
  password               = random_password.analytics_db.result
  db_subnet_group_name   = aws_db_subnet_group.analytics.name
  vpc_security_group_ids = [aws_security_group.analytics_db.id]
  skip_final_snapshot    = true # set false once this is a real environment
  publicly_accessible    = false
}
