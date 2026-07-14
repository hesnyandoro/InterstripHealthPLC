# Interstrip Health PLC — Platform Monorepo

Microservices architecture, one repo, independently deployed services on EKS.
See `infra/terraform` for cluster/DB provisioning and `services/<name>/k8s` for
each service's own manifests.

## Structure

```
infra/terraform/       VPC, EKS cluster, ECR repos, per-service RDS instances
infra/k8s/base/        Cluster-wide manifests (namespace, ingress controller, etc.)
services/analytics/    FastAPI service — hospital dashboards (first service built)
services/<other>/      claimguard, medsource, envihealth, auth, gateway — scaffold as they're built
apps/web-marketing/    Next.js public site (deployed separately to Vercel)
.github/workflows/     One path-filtered workflow per service
```

## First-time infra setup

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply

# then, to point kubectl at the new cluster:
aws eks update-kubeconfig --region af-south-1 --name ihp-dev

kubectl apply -f ../k8s/base/namespace.yaml
```

## Running everything locally

```bash
docker compose up --build
# postgres     → localhost:5432 (databases: ihp_auth, ihp_analytics)
# auth         → http://localhost:8001/docs
# analytics    → http://localhost:8002/docs
```

Bind mounts on `app/` give both services hot reload — edit code, the running
container picks it up.

First run only, create tables (no migrations tool yet — see the note in each
service's `create_tables.py`):

```bash
docker compose exec auth python create_tables.py
docker compose exec analytics python create_tables.py
```

### End-to-end smoke test

```bash
# 1. Register a hospital org + admin user, get a token back
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"org_name":"Nairobi Hospital","org_type":"hospital","email":"admin@nairobihosp.example","password":"changeme123"}'

# 2. Call Analytics with that token — org scoping happens automatically from the JWT
curl http://localhost:8002/api/v1/dashboard/facilities \
  -H "Authorization: Bearer <access_token_from_step_1>"
# → [] since no Facility rows exist yet; insert one via psql or a script to test occupancy
```

Both services must share the same `JWT_SECRET` — docker-compose.yml already sets
the same value for both; keep them in sync if you change it.

## Adding a new microservice

1. Copy `services/analytics` as a starting template (Dockerfile + k8s/ pattern)
2. Add its name to `service_names` in `infra/terraform/variables.tf` → `terraform apply` creates its ECR repo
3. Copy `infra/terraform/rds-analytics.tf` → `rds-<service>.tf` if it needs its own database
4. Copy `.github/workflows/analytics.yml`, rename, update `ECR_REPOSITORY`/`SERVICE_DIR`/paths filter

## Required GitHub secrets

- `AWS_DEPLOY_ROLE_ARN` — an IAM role GitHub Actions assumes via OIDC (no static AWS keys in the repo)
