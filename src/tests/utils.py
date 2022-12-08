import asyncio

import httpx


async def slow_endpoint(request: httpx.Request):
    timeout = None
    if "timeout" in request.extensions:
        timeout = request.extensions["timeout"].get("read")
    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=timeout)
    except:
        raise httpx.ReadTimeout("")
    return httpx.Response(status_code=200, json={"time": 2000})


async def unavailable_endpoint(request: httpx.Request):
    return httpx.Response(status_code=500)


async def slow_and_unavailable_endpoint(request: httpx.Request):
    timeout = None
    if "timeout" in request.extensions:
        timeout = request.extensions["timeout"].get("read")
    try:
        await asyncio.wait_for(asyncio.sleep(0.5), timeout=timeout)
    except:
        raise httpx.ReadTimeout("")
    return httpx.Response(status_code=500)
