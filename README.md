# Django Celery Microservice Deployment Guide
Practical Assessment for AWS Developer Role

## System Architecture
![Architecture Diagram: GitHub → CI/CD → Docker Hub → AWS EC2 (Terraform provisioned)]

## Prerequisites
1. Infrastructure Tools
- AWS Account with IAM user (programmatic access enabled)
- AWS CLI configured
- Terraform installed
- Docker Hub account

2. Development Environment
- Python 3.9+
- Git

## Local Development Setup
1. Fork and clone the repository:
```bash
git clone https://github.com/<username>/hng_boilerplate_python_fastapi_web.git
cd django-microservice
```

2. Create a .env file from .env.sample:
```bash
cp .env.sample .env # Edit with your actual values
```

3. Start services locally
```bash
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

4. Verify local operation
API Docs: http://localhost:8000/

5. Clean up docker
```bash
docker-compose down
```

## Production Deployment
### Infrastructure Provisioning
1. Initialize Terraform
```bash
cd terraform/
terraform init
terraform validate
```

2. Review execution plan
```bash
terraform plan
```

3. Deploy Infrastructure
```bash
terraform apply -auto-approve
```

### CI/CD Configuration
1. GitHub Secrets Setup
Navigate to: Settings → Secrets → Actions
Add these required secrets:
```
DOCKER_HUB_USERNAME=your-docker-hub-username
DOCKER_HUB_TOKEN=your-docker-hub-password
EC2_SSH_KEY=your-base64-encoded-PEM-key
EC2_HOST=your-public-EC2-IP
```

2. GitHub Variables Setup
Under Settings → Environments → Production:
```
SECRET_KEY=your_secret_key
DEBUG=False
DB_NAME=your_db_name
DB_HOST=postgres
DB_PORT=5432
DB_USER=your_db_user
DB_PASS=your_secure_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_password
```

3. Push to GitHub
```bash
git push origin main
```

4. Check pipeline status
Monitor workflow runs under GitHub Actions tab

5. Validate services
```bash
ssh -i key.pem ubuntu@<EC2_IP>
docker ps  # Should show web, worker, and redis containers
```

6. Test endpoints
```bash
# Submit task
curl -X POST http://<EC2_IP>:8000/api/process/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","message":"Hello World"}'

# Check status (replace with actual task_id)
curl http://<EC2_IP>:8000/api/status/<task_id>/
```

## Troubleshooting Common Issues
1. Migrations not applying:
```bash
ssh ubuntu@<EC2_IP> "docker-compose -f /app/docker-compose.prod.yml exec web python manage.py migrate"
```

2. Celery worker offline:
Check Redis connection in worker logs:
```bash
docker logs <worker_container_id>
```

## Architectural Notes
1. Separation of Concerns:
- Web service handles HTTP requests
- Worker service processes background tasks
- Redis serves as message broker

2. Security:
- All sensitive data stored in environment variables and secrets
- Minimal exposed ports (only 8000 for HTTP)

3. Monitoring:
- CloudWatch to monitor EC2 instance health

This solution demonstrates a complete implementation of the requested microservice with proper DevOps practices and AWS deployment.
Please note that you should replace placeholders with your actual values. Also, ensure you have the necessary permissions
