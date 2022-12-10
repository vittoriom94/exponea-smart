import time

import httpx
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import fastapi
import uvicorn
from fastapi import FastAPI, Depends

import api
import exceptions
import models
import settings
import utils
from models import TimeoutParameter

settings.configure_logger()

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)


@app.get("/api/smart", response_model=models.ApiSmartResponse)
async def api_smart(timeout: int = TimeoutParameter, client: httpx.AsyncClient = Depends(utils.get_async_client)):
    """
    Retrieve data from the exponea API endpoint
    :param timeout: maximum time in milliseconds for this function
    :param client: httpx.AsyncClient used to send requests to the exponea endpoint
    :return: execution time of this function, and data from the exponea api endpoint.
    """
    try:
        timeout_in_seconds = timeout/1000
        start = time.perf_counter()
        response_body = await api.get_data(timeout_in_seconds-settings.TIMEOUT_TOLERANCE, client)
        end = time.perf_counter()
        return models.ApiSmartResponse(time=int((end-start)*1000), api=response_body)
    except exceptions.UnsuccessfulApiError:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not reach Exponea API successfully")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
