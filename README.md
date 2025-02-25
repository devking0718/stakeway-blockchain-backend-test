# Stakeway - Blockchain Backend Engineer Technical Assessment

## Project Overview

Project consists of 3 sections.
1. Backend API
2. Deployment & Monitoring
3. Blockchain Integration

## Section 1 - Backend API

This project is built using Python and FastAPI using Docker container.

To run the project, build the docker image and run the container.

### Setup instructions

```bash
# Build the Docker image
docker build -t stakeway-test .

# Run the container
docker run -d -p 80:8000 stakeway-test
```

### API documentation

The API provides endpoints for validator key generation and monitoring.

#### 1. Create Validator Request
- **URL**: `/validators`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "num_validators": integer,
    "fee_recipient": string
  }
  ```
  - `num_validators`: Number of validator keys to generate (must be > 0)
  - `fee_recipient`: Ethereum address for fee recipient (must be valid ETH address)
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "request_id": string,
      "message": "Validator creation in progress"
    }
    ```
- **Error Response**:
  - **Code**: 422
  - **Content**: Validation error details

**Example Request:**
```bash
curl -X POST http://localhost:80/validators \
  -H "Content-Type: application/json" \
  -d '{
    "num_validators": 2,
    "fee_recipient": "0x1234567890abcdef1234567890abcdef12345678"
  }'
```

**Example Response:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Validator creation in progress"
}
```

#### 2. Get Validator Request Status
- **URL**: `/validators/{request_id}`
- **Method**: `GET`
- **URL Parameters**: `request_id` - ID received from create request
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "status": string,
      "keys": array[string] | null,
      "message": string | null
    }
    ```
  - `status`: One of "started", "successful", or "failed"
  - `keys`: Array of generated validator keys (only present when status is "successful")
  - `message`: Error message (only present when status is "failed")
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"detail": "Request not found"}`

**Example Request:**
```bash
curl http://localhost:80/validators/550e8400-e29b-41d4-a716-446655440000
```

**Example Responses:**

In Progress:
```json
{
  "status": "started",
  "keys": null
}
```

Successful:
```json
{
  "status": "successful",
  "keys": [
    "0x8f5b3d38cd68f79d1b7c8314c3a5e4560c45c24655c1c8fc628eed5caa290d8c",
    "0x7a2e121f6d2f3e8c8e09c8f6d2e3a8c7e5d4b1a9c8e7d6f3a2e1d4c7b0a9f8e7"
  ]
}
```

Failed:
```json
{
  "status": "failed",
  "message": "Error generating validator keys"
}
```
### Environment setup details

Before running the application, you need to set up the environment:

- On Windows:
  ```bash
  setup.bat
  ```

- On Linux/Mac:
  ```bash
  ./setup.sh
  ```

This will setup virtual environment and install all required dependencies.


### Unit test coverage

Unit tests are located in the `tests` folder.

To run the tests, use the following command:

```bash
pytest -v -s
```

## Section 2 - Deployment & Monitoring

The application is containerized and deployed using Kubernetes. The deployment configuration and monitoring setup are provided in the following sections.

### Kubernetes Deployment

Kubernetes YAML files are located in the `./k8s` directory:

- `deployment.yaml` - Defines the deployment configuration including replicas, container specs, and resource limits
- `service.yaml` - Exposes the application via a LoadBalancer service
- `configmap.yaml` - Contains application configuration 

### Monitoring Stack

Prometheus and Grafana configurations are also located in `./k8s`:

Here are PromQL queries used to monitor the application:

- Total requests per second:
  ```
  rate(http_requests_total[5m])
  ```

- Average request duration:
  ```
  rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
  ```   

- Error rate:
  ```
  sum(rate(http_requests_total{status=~"5.*"}[5m])) / sum(rate(http_requests_total[5m])) * 100
  ```

### Docker Image

The Docker image for this service is publicly available on Docker Hub:
https://hub.docker.com/r/devking0718/stakeway-test

## Section 3 - Blockchain Integration

The blockchain integration is implemented in `app/eth_staking.py` which simulates staking operations.

### Environment Setup

Create a `.env` file based on the provided `.env_sample` template:

### Run the staking script

To run the staking script, use the following command:

```bash
python app/eth_staking.py
```







