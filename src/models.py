from fastapi import Query
from pydantic import BaseModel

import settings

MIN_TIMEOUT_MS = settings.MAX_FIRST_TIMEOUT_MS + 200

TimeoutParameter = Query(
    ge=MIN_TIMEOUT_MS,
    title="Timeout (ms)",
    description="Maximum response time in milliseconds."
)


class ApiSmartResponse(BaseModel):
    time: int
    api: dict
