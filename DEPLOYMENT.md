# Deployment Guide

This guide provides step-by-step instructions for deploying the Health Monitoring System on various platforms.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)

## Local Development

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup Steps

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd health-monitoring-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train models**
   ```bash
   python train_models.py
   ```

5. **Start the server**
   ```bash
   python main.py
   ```

6. **Test the system**
   ```bash
   python test_api.py
   ```

7. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Frontend: Open `frontend/index.html` in browser

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Train models (first time only)**
   ```bash
   docker-compose exec health-monitor-api python train_models.py
   ```

3. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

### Manual Docker Build

1. **Build the image**
   ```bash
   docker build -t health-monitor .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/models:/app/models health-monitor
   ```

### Production Docker Deployment

1. **Use production profile**
   ```bash
   docker-compose --profile production up -d
   ```

2. **Set up SSL certificates**
   ```bash
   mkdir ssl
   # Add your SSL certificates to the ssl directory
   ```

3. **Configure Nginx**
   Create `nginx.conf`:
   ```nginx
   events {
       worker_connections 1024;
   }
   
   http {
       upstream health_monitor {
           server health-monitor-api:8000;
       }
   
       server {
           listen 80;
           server_name your-domain.com;
           return 301 https://$server_name$request_uri;
       }
   
       server {
           listen 443 ssl;
           server_name your-domain.com;
   
           ssl_certificate /etc/nginx/ssl/cert.pem;
           ssl_certificate_key /etc/nginx/ssl/key.pem;
   
           location / {
               proxy_pass http://health_monitor;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }
       }
   }
   ```

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS Lambda + API Gateway

1. **Create deployment package**
   ```bash
   pip install -r requirements.txt -t package/
   cp -r app package/
   cp main.py package/
   cp config.py package/
   cd package
   zip -r ../health-monitor-lambda.zip .
   ```

2. **Create Lambda function**
   - Runtime: Python 3.9
   - Handler: main.handler
   - Memory: 512 MB
   - Timeout: 30 seconds

3. **Configure API Gateway**
   - Create REST API
   - Add resources and methods
   - Enable CORS

#### Option 2: AWS ECS/Fargate

1. **Create ECR repository**
   ```bash
   aws ecr create-repository --repository-name health-monitor
   ```

2. **Build and push image**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t health-monitor .
   docker tag health-monitor:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/health-monitor:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/health-monitor:latest
   ```

3. **Create ECS cluster and service**
   - Use the provided `docker-compose.yml` as reference
   - Configure load balancer
   - Set up auto-scaling

### Google Cloud Platform

#### Option 1: Cloud Run

1. **Enable required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/health-monitor
   gcloud run deploy health-monitor \
     --image gcr.io/PROJECT-ID/health-monitor \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

#### Option 2: GKE (Kubernetes)

1. **Create cluster**
   ```bash
   gcloud container clusters create health-monitor-cluster \
     --num-nodes=3 \
     --zone=us-central1-a
   ```

2. **Deploy with kubectl**
   ```bash
   kubectl apply -f k8s/
   ```

### Azure

#### Option 1: Azure Container Instances

1. **Build and push to Azure Container Registry**
   ```bash
   az acr build --registry <registry-name> --image health-monitor .
   ```

2. **Deploy container instance**
   ```bash
   az container create \
     --resource-group <resource-group> \
     --name health-monitor \
     --image <registry-name>.azurecr.io/health-monitor:latest \
     --ports 8000 \
     --dns-name-label health-monitor
   ```

#### Option 2: Azure Kubernetes Service

1. **Create AKS cluster**
   ```bash
   az aks create --resource-group <resource-group> --name health-monitor-cluster --node-count 3
   ```

2. **Deploy application**
   ```bash
   kubectl apply -f k8s/
   ```

### PythonAnywhere

1. **Upload files**
   - Upload all source files to your PythonAnywhere account
   - Use the file browser or Git integration

2. **Install dependencies**
   ```bash
   pip install --user -r requirements.txt
   ```

3. **Configure WSGI file**
   Create `passenger_wsgi.py`:
   ```python
   import sys
   import os
   
   # Add your project directory to Python path
   sys.path.insert(0, '/home/yourusername/health-monitoring-system')
   
   from main import app
   
   application = app
   ```

4. **Train models**
   ```bash
   python train_models.py
   ```

5. **Configure web app**
   - Set source code directory
   - Set working directory
   - Configure WSGI file path

## Production Considerations

### Security

1. **Environment Variables**
   ```bash
   # Production environment variables
   export DEBUG=False
   export HOST=0.0.0.0
   export PORT=8000
   export REDIS_HOST=your-redis-host
   export REDIS_PASSWORD=your-redis-password
   ```

2. **SSL/TLS**
   - Use HTTPS in production
   - Configure SSL certificates
   - Enable HSTS headers

3. **Authentication**
   - Implement API key authentication
   - Add rate limiting
   - Use JWT tokens for user sessions

### Performance

1. **Caching**
   - Enable Redis caching
   - Cache model predictions
   - Use CDN for static files

2. **Load Balancing**
   - Use multiple instances
   - Configure health checks
   - Set up auto-scaling

3. **Monitoring**
   - Set up logging (ELK stack)
   - Monitor response times
   - Track error rates
   - Set up alerts

### Data Management

1. **Database**
   - Use PostgreSQL for production data
   - Implement data backup strategy
   - Set up data retention policies

2. **Model Management**
   - Version control for models
   - A/B testing framework
   - Model performance monitoring

### Backup and Recovery

1. **Regular Backups**
   ```bash
   # Backup models and data
   tar -czf backup-$(date +%Y%m%d).tar.gz models/ data/
   ```

2. **Disaster Recovery**
   - Document recovery procedures
   - Test backup restoration
   - Maintain multiple backup locations

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```bash
   # Check if models exist
   ls -la models/
   
   # Retrain models if needed
   python train_models.py
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

3. **Memory Issues**
   - Increase container memory
   - Optimize model loading
   - Use model quantization

4. **Performance Issues**
   - Check response times
   - Monitor resource usage
   - Optimize database queries

### Logs and Debugging

1. **Enable Debug Mode**
   ```bash
   export DEBUG=True
   python main.py
   ```

2. **Check Application Logs**
   ```bash
   # Docker logs
   docker-compose logs health-monitor-api
   
   # Kubernetes logs
   kubectl logs deployment/health-monitor
   ```

3. **Health Check**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Test with the provided test script
4. Create an issue in the repository

## Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Configure CI/CD pipeline
3. Implement user authentication
4. Add advanced features
5. Scale based on usage patterns




