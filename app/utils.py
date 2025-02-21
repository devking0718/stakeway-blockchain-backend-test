import uuid
import random
import string
import asyncio

def generate_uuid():
    return str(uuid.uuid4())

def generate_mock_key(length=48):
    return ''.join(random.choices(string.hexdigits, k=length))

async def simulate_key_generation():
    await asyncio.sleep(0.02)  # 20ms delay
    return generate_mock_key() 