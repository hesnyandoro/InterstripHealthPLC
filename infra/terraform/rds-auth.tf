resource "aws_db_subnet_group" "auth" {
  name       = "${var.project}-${var.environment}-auth-db"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "auth_db" {
  name   = "${var.project}-${var.environment}-auth-db-sg"
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

resource "random_password" "auth_db" {
  length  = 24
  special = false
}

resource "aws_secretsmanager_secret" "auth_db" {
  name = "${var.project}-${var.environment}-auth-db-credentials"
}

resource "aws_secretsmanager_secret_version" "auth_db" {
  secret_id = aws_secretsmanager_secret.auth_db.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.auth_db.result
    host     = aws_db_instance.auth.address
    port     = 5432
    dbname   = "ihp_auth"
  })
}

resource "aws_db_instance" "auth" {
  identifier              = "${var.project}-${var.environment}-auth"
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  db_name                 = "ihp_auth"
  username                = var.db_username
  password                = random_password.auth_db.result
  db_subnet_group_name    = aws_db_subnet_group.auth.name
  vpc_security_group_ids  = [aws_security_group.auth_db.id]
  skip_final_snapshot     = true
  publicly_accessible     = false
}

# --- Shared JWT signing secret --------------------------------------------
# Every service mounts this same secret (K8s Secret name "jwt-signing-key") to
# verify tokens the auth service issues. Rotate by updating this value and
# rolling all service deployments — there's no downtime-free rotation here yet
# since it's a single shared HS256 secret (see note in auth/app/security.py
# about moving to RS256 + JWKS once that becomes worth the complexity).
resource "random_password" "jwt_signing_key" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "jwt_signing_key" {
  name = "${var.project}-${var.environment}-jwt-signing-key"
}

resource "aws_secretsmanager_secret_version" "jwt_signing_key" {
  secret_id     = aws_secretsmanager_secret.jwt_signing_key.id
  secret_string = jsonencode({ JWT_SECRET = random_password.jwt_signing_key.result })
}
