import asyncio
import httpx

import exceptions
import settings
import logging


async def get_data(available_time: float, client: httpx.AsyncClient) -> dict:
    successful_response_body: dict | None
    try:
        response = await client.get(settings.EXPONEA_ENDPOINT, timeout=settings.MAX_FIRST_TIMEOUT_MS/1000)
        logging.info("Received first response")
        response.raise_for_status()
        logging.info("First response OK")
        successful_response_body = response.json()
    except (httpx.TimeoutException, httpx.HTTPStatusError) as ex:
        logging.warning(f"First response unsuccessful: {type(ex)}")
        successful_response_body = await run_two_api_calls(available_time-settings.MAX_FIRST_TIMEOUT_MS/1000, client)

    if not successful_response_body:
        logging.error("No successful response")
        raise exceptions.UnsuccessfulApiError()
    return successful_response_body


async def run_two_api_calls(timeout: int, client: httpx.AsyncClient) -> dict | None:
    response_data = None
    tasks = [asyncio.create_task(client.get(settings.EXPONEA_ENDPOINT, timeout=timeout)) for _ in range(settings.RETRIES)]
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
