# AWS API Deployment Guide
## SOYL-MODEL Emotion Detection API

This guide provides instructions for deploying the SOYL-MODEL emotion detection API to AWS using API Gateway and backend compute services.

---

## 📋 Architecture Overview

The SOYL-MODEL API integrates three emotion detection modules:
- **Vision Module**: TensorFlow/Keras model for facial emotion detection
- **Voice Module**: Audio processing for voice emotion analysis
- **Text Module**: Transformer-based sentiment analysis (DistilBERT/similar)

**Current API Endpoints:**
- `POST /getEmotionState` - Fuses emotion data from multiple modules
- `GET /` - Health check endpoint

---

## 🎯 Infrastructure Recommendation

### **Recommended: EC2/ECS with GPU Support**

**Why EC2/ECS over Lambda:**
1. **GPU Requirements**: 
   - Vision module uses TensorFlow/Keras models that benefit significantly from GPU acceleration
   - Text module uses transformer models (DistilBERT/similar) that perform much better on GPU
   - Real-time inference requires low latency, which GPUs provide

2. **Model Loading**:
   - Models need to be loaded into memory for fast inference
   - Lambda cold starts (5-10 seconds) are too slow for real-time use
   - EC2 allows persistent model loading

3. **Resource Requirements**:
   - Multiple models loaded simultaneously (vision, text, potentially voice)
   - Memory requirements: ~4-8GB for all models
   - Lambda's 10GB memory limit may be tight

4. **Timeout Considerations**:
   - Video/audio processing can take several seconds
   - Lambda's 15-minute timeout is sufficient, but GPU instances provide better performance

**Recommended Instance Types:**
- **Development/Testing**: `g4dn.xlarge` (1 GPU, 4 vCPU, 16GB RAM) - ~$0.50/hour
- **Production**: `g4dn.2xlarge` (1 GPU, 8 vCPU, 32GB RAM) - ~$0.75/hour
- **High Traffic**: `g5.xlarge` (1 GPU, 4 vCPU, 16GB RAM) - ~$1.00/hour

**Alternative: ECS/Fargate with GPU Tasks**
- Better for container orchestration
- Auto-scaling capabilities
- More cost-effective for variable traffic

### **Alternative: Lambda with Containers (If GPU Not Required)**

**Use Lambda if:**
- You're willing to optimize models for CPU inference
- Traffic is sporadic (cost savings)
- You can accept 5-10 second cold starts
- Models are lightweight enough for CPU

**Limitations:**
- No GPU support in Lambda
- 15-minute timeout maximum
- 10GB memory limit
- Container image size limit: 10GB

---

## 🏗️ Deployment Architecture

```
┌─────────────────┐
│  API Gateway     │
│  (REST API)      │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  EC2/ECS        │
│  (FastAPI App)  │
│  - GPU Instance │
│  - Docker Image │
└────────┬─────────┘
         │
         ├──► Vision Module (TensorFlow)
         ├──► Voice Module (Librosa)
         └──► Text Module (Transformers)
```

---

## 📦 Prerequisites

### AWS Account Setup
1. Create an IAM user with the following permissions:
   - `AmazonEC2FullAccess` (for EC2 deployment)
   - `AmazonECS_FullAccess` (for ECS deployment)
   - `AmazonAPIGatewayAdministrator` (for API Gateway)
   - `AmazonVPCFullAccess` (for networking)
   - `AmazonS3FullAccess` (for storing model files)
   - `CloudWatchLogsFullAccess` (for logging)

2. Install AWS CLI:
   ```bash
   pip install awscli
   aws configure
   ```

3. Install Docker (for containerization):
   - Windows: Docker Desktop
   - Linux: `sudo apt-get install docker.io`

---

## 🚀 Deployment Steps

### Step 1: Prepare Docker Image

Create a `Dockerfile` in the project root:

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install TensorFlow with GPU support
RUN pip3 install tensorflow[and-cuda]

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and test locally:
```bash
docker build -t soyl-model-api:latest .
docker run -p 8000:8000 soyl-model-api:latest
```

### Step 2: Push Docker Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name soyl-model-api

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag soyl-model-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/soyl-model-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/soyl-model-api:latest
```

### Step 3: Deploy to EC2 (Option A)

#### 3.1 Launch EC2 Instance
1. Go to EC2 Console → Launch Instance
2. Choose **Deep Learning AMI (Ubuntu)** or **Amazon Linux 2023**
3. Select instance type: `g4dn.xlarge` (or `g4dn.2xlarge` for production)
4. Configure security group:
   - Inbound: Port 8000 from API Gateway IP ranges
   - Inbound: Port 22 (SSH) from your IP
5. Launch instance and save key pair

#### 3.2 Setup EC2 Instance
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<instance-ip>

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu
sudo systemctl start docker

# Install NVIDIA Container Toolkit (for GPU support)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Pull and run container
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker pull <account-id>.dkr.ecr.us-east-1.amazonaws.com/soyl-model-api:latest
docker run -d --gpus all -p 8000:8000 --name soyl-api <account-id>.dkr.ecr.us-east-1.amazonaws.com/soyl-model-api:latest
```

#### 3.3 Setup Auto-start (Optional)
Create systemd service:
```bash
sudo nano /etc/systemd/system/soyl-api.service
```

```ini
[Unit]
Description=SOYL Model API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/docker start soyl-api
ExecStop=/usr/bin/docker stop soyl-api
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable soyl-api
sudo systemctl start soyl-api
```

### Step 4: Deploy to ECS with GPU (Option B - Recommended for Production)

#### 4.1 Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name soyl-model-cluster
```

#### 4.2 Create Task Definition
Create `task-definition.json`:
```json
{
  "family": "soyl-model-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["EC2"],
  "cpu": "4096",
  "memory": "8192",
  "containerDefinitions": [
    {
      "name": "soyl-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/soyl-model-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "resourceRequirements": [
        {
          "type": "GPU",
          "value": "1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/soyl-model-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### 4.3 Create ECS Service
```bash
aws ecs create-service \
  --cluster soyl-model-cluster \
  --service-name soyl-model-api \
  --task-definition soyl-model-api \
  --desired-count 1 \
  --launch-type EC2 \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Step 5: Setup API Gateway

#### 5.1 Create REST API
1. Go to API Gateway Console
2. Create new REST API
3. Create resource: `/getEmotionState`
4. Create POST method
5. Integration type: HTTP
6. Endpoint URL: `http://<ec2-ip>:8000/getEmotionState` (or ECS ALB endpoint)
7. Enable CORS if needed

#### 5.2 Deploy API
1. Create new stage: `prod` or `dev`
2. Deploy API
3. Note the Invoke URL

#### 5.3 Setup Custom Domain (Optional)
1. Create custom domain in API Gateway
2. Configure SSL certificate (ACM)
3. Map domain to API stage

### Step 6: Configure Security

#### Security Group Rules
- Allow inbound: Port 8000 from API Gateway VPC
- Allow inbound: Port 22 (SSH) from your IP only
- Allow outbound: All traffic (for model downloads, etc.)

#### IAM Roles
- EC2/ECS task role needs access to:
  - CloudWatch Logs
  - S3 (if storing models there)
  - Secrets Manager (if storing API keys)

---

## 🔧 API Endpoint Implementation

### Current Endpoints to Implement

1. **POST /getEmotionState**
   - Accepts: `{ "modules": [{"valence": float, "arousal": float, "confidence": float, "source": str}] }`
   - Returns: Fused emotion state

2. **POST /analyzeFace** (New - to add)
   - Accepts: Image file (multipart/form-data)
   - Returns: Face emotion analysis

3. **POST /analyzeVoice** (New - to add)
   - Accepts: Audio file (WAV/MP3)
   - Returns: Voice emotion analysis

4. **POST /analyzeText** (New - to add)
   - Accepts: `{ "text": "string" }`
   - Returns: Text sentiment analysis

5. **GET /health**
   - Returns: API health status

### Example FastAPI Endpoint Implementation

```python
from fastapi import FastAPI, UploadFile, File
from modules.vision.face_emotion import infer_from_frame
from modules.voice.voice_emotion import infer_from_audio_chunk
from modules.text.text_sentiment import infer_from_text
import cv2
import numpy as np

@app.post("/analyzeFace")
async def analyze_face(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = infer_from_frame(frame)
    return result

@app.post("/analyzeVoice")
async def analyze_voice(file: UploadFile = File(...)):
    # Process audio file
    # Return emotion analysis
    pass

@app.post("/analyzeText")
async def analyze_text(text: str):
    result = infer_from_text(text)
    return result
```

---

## 📊 Monitoring & Logging

### CloudWatch Setup
1. Create Log Group: `/ecs/soyl-model-api` (for ECS) or `/ec2/soyl-api` (for EC2)
2. Monitor:
   - API request latency
   - Error rates
   - GPU utilization
   - Memory usage

### Health Checks
- Implement `/health` endpoint
- Setup API Gateway health check
- Configure auto-scaling based on CPU/GPU utilization

---

## 💰 Cost Estimation

### EC2 g4dn.xlarge (Development)
- Instance: ~$0.50/hour = ~$360/month
- Data transfer: ~$10-50/month
- **Total: ~$370-410/month**

### EC2 g4dn.2xlarge (Production)
- Instance: ~$0.75/hour = ~$540/month
- Data transfer: ~$20-100/month
- **Total: ~$560-640/month**

### ECS with Auto-scaling
- Pay only for running tasks
- Can scale down during low traffic
- **Estimated: ~$300-500/month** (variable)

---

## ✅ Checklist for API Developer

- [ ] Review and understand the three emotion modules (vision, voice, text)
- [ ] Implement new API endpoints (`/analyzeFace`, `/analyzeVoice`, `/analyzeText`)
- [ ] Update `/getEmotionState` to accept file uploads or integrate module calls
- [ ] Add proper error handling and validation
- [ ] Implement request/response logging
- [ ] Add API authentication (API keys or JWT tokens)
- [ ] Write unit tests for all endpoints
- [ ] Create Docker image and test locally
- [ ] Push Docker image to ECR
- [ ] Deploy to EC2 or ECS
- [ ] Configure API Gateway integration
- [ ] Setup CloudWatch monitoring
- [ ] Test all endpoints with real data
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Setup CI/CD pipeline (optional but recommended)

---

## 🐛 Troubleshooting

### GPU Not Detected
- Ensure NVIDIA drivers are installed on EC2
- Check Docker GPU support: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`
- Verify ECS task definition includes GPU resource requirement

### Model Loading Errors
- Check model files are in correct directory
- Verify file permissions
- Ensure sufficient memory allocated

### API Gateway Timeout
- Increase timeout in API Gateway settings (max 29 seconds)
- Consider using async processing for long-running tasks
- Implement request queuing if needed

### High Latency
- Enable GPU acceleration
- Optimize model inference (quantization, batch processing)
- Use connection pooling
- Consider model caching strategies

---

## 📚 Additional Resources

- [AWS EC2 GPU Instances](https://aws.amazon.com/ec2/instance-types/g4/)
- [ECS GPU Tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-gpu.html)
- [API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 📝 Notes

- **Model Files**: Ensure `multi_emotion_model_stable.h5` and other model files are included in Docker image or stored in S3 and downloaded at startup
- **Environment Variables**: Use AWS Secrets Manager or Parameter Store for API keys and configuration
- **Scaling**: Consider using Application Load Balancer (ALB) in front of ECS for better load distribution
- **Security**: Implement API authentication before production deployment
- **Cost Optimization**: Use Spot Instances for development/testing (up to 90% savings)

---

**Last Updated**: November 2024  
**Maintained By**: SOYL R&D Team

