from typing import List
from uuid import uuid4

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

APP_INSTANCE_ID = uuid4()


def calculate_entropy(values: List[int]) -> float:
    # Compute the frequency of each number
    _, counts = np.unique(values, return_counts=True)
    # Convert the frequencies to probabilities
    probabilities = counts / len(values)
    # Compute the entropy
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy


app = FastAPI()


class EntropyRequest(BaseModel):
    values: List[int]


@app.get("/")
async def read_root():
    return {"message": "Hello World", 'instance_id': APP_INSTANCE_ID}


@app.post("/entropy")
async def entropy(request: EntropyRequest):
    return {'entropy': calculate_entropy(request.values), 'instance_id': APP_INSTANCE_ID}
