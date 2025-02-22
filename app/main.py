from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import asyncio
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from .database import get_db, init_db
from .models import ValidatorRequest, ValidatorKey, RequestStatus
from .schemas import (
    ValidatorRequestCreate,
    ValidatorRequestResponse,
    ValidatorStatusResponse,
    HealthResponse
)
from .utils import generate_uuid, simulate_key_generation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    # Add any cleanup code here if needed

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    if request.url.path != '/metrics':
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
    
    return response

@app.get('/metrics')
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

async def process_validator_request(
    request_id: str,
    num_validators: int,
    fee_recipient: str,
    db: Session
):
    try:
        keys = []
        for _ in range(num_validators):
            key = await simulate_key_generation()
            validator_key = ValidatorKey(
                key=key,
                request_id=request_id,
                fee_recipient=fee_recipient
            )
            db.add(validator_key)
            keys.append(key)
        
        request = db.query(ValidatorRequest).filter_by(request_id=request_id).first()
        request.status = RequestStatus.SUCCESSFUL
        db.commit()
        logger.info(f"Successfully processed request {request_id}")
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}")
        request = db.query(ValidatorRequest).filter_by(request_id=request_id).first()
        request.status = RequestStatus.FAILED
        request.error_message = str(e)
        db.commit()

@app.post("/validators", response_model=ValidatorRequestResponse)
async def create_validator_request(
    request: ValidatorRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    request_id = generate_uuid()
    validator_request = ValidatorRequest(
        request_id=request_id,
        num_validators=request.num_validators,
        fee_recipient=request.fee_recipient,
        status=RequestStatus.STARTED
    )
    
    db.add(validator_request)
    db.commit()
    
    background_tasks.add_task(
        process_validator_request,
        request_id,
        request.num_validators,
        request.fee_recipient,
        db
    )
    
    return ValidatorRequestResponse(
        request_id=request_id,
        message="Validator creation in progress"
    )

@app.get("/validators/{request_id}", response_model=ValidatorStatusResponse)
async def get_request_status(request_id: str, db: Session = Depends(get_db)):
    request = db.query(ValidatorRequest).filter_by(request_id=request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status == RequestStatus.SUCCESSFUL:
        keys = [key.key for key in db.query(ValidatorKey).filter_by(request_id=request_id).all()]
        return ValidatorStatusResponse(status=request.status, keys=keys)
    elif request.status == RequestStatus.FAILED:
        return ValidatorStatusResponse(
            status=request.status,
            message=request.error_message or "Error processing request"
        )
    else:
        return ValidatorStatusResponse(status=request.status)

@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return HealthResponse(status="healthy", database="connected")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(status="unhealthy", database="disconnected") 