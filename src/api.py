import asyncio
import httpx

import exceptions
import settings
import logging


class ClientInstance:
    _client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls):
        if not cls._client:
            cls._client = httpx.AsyncClient()
            logging.debug("Created httpx.AsyncClient")
        return cls._client

    @classmethod
    async def stop(cls):
        if cls._client:
            await cls._client.aclose()
            logging.debug("Closed httpx.AsyncClient")


client = ClientInstance()


async def get_data(available_time: float) -> dict:
    successful_response_body: dict | None
    try:
        response = await client.get_client().get(settings.EXPONEA_ENDPOINT, timeout=settings.MAX_FIRST_TIMEOUT_MS/1000)
        logging.info("Received first response")
        response.raise_for_status()
        logging.info("First response OK")
        successful_response_body = response.json()
    except (httpx.TimeoutException, httpx.HTTPStatusError) as ex:
        logging.warning(f"First response unsuccessful: {type(ex)}")
        successful_response_body = await run_two_api_calls(available_time-settings.MAX_FIRST_TIMEOUT_MS/1000)

    if not successful_response_body:
        logging.error("No successful response")
        raise exceptions.UnsuccessfulApiError()
    return successful_response_body


async def run_two_api_calls(timeout: int) -> dict | None:
    response_data = None
    tasks = [asyncio.create_task(client.get_client().get(settings.EXPONEA_ENDPOINT, timeout=timeout)) for _ in range(settings.RETRIES)]
    for task in asyncio.as_completed(tasks):
        try:
            response = await task
            response.raise_for_status()
            cancel_tasks(tasks)
            response_data = response.json()
        except asyncio.exceptions.CancelledError:
            pass
        except (httpx.TimeoutException, httpx.HTTPStatusError) as ex:
            logging.warning(f"Response unsuccessful: {type(ex)}")
    return response_data


def cancel_tasks(tasks: list) -> None:
    for task in tasks:
        task.cancel()
