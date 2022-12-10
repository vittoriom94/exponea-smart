# Exponea Smart

## Instruction

### Run with docker:

Be sure that the following ports are free: `8000, 8089, 9411`

Use `docker-compose up` to launch all the required services.

Go to `http://localhost:8000/api/smart` to test the service.

`timeout` query param is required, it's unit of measure is milliseconds.

To check the telemetry go to `http://localhost:9411` as you can reach the Zipkin service launched by docker-compose.

For a stress test, you can use Locust. The service is already available at `http://localhost:8089`

## Architecture

#### Overview
The exercise is presented as a FastAPI application with a single endpoint.

As per requirements, the only endpoint available for the app is `/api/smart`. It is required to supply the `timeout` query parameter as the maximum time in milliseconds to obtain a response from the server.

#### API response

The response will either be successful or failed:
- Success: `200`. Reponse body: `{"time": time_in_ms, "api": response_from_exponea_endpoint}`
- Fail: `503`. Returned when the exponea endpoint is not able to fullfil the request in time or is not available for all 3 calls to the endpoint.

#### Data flow

Following the requirements, the application will send a request to the exponea API with a 300ms timeout. If the request cannot be fulfilled in time or fails, two more will be sent concurrently, returning the first one and canceling the other.

A timeout has been applied to both the `api.get_data` function and the `httpx.client.get` calls to the external endpoint. The reason is that this avoids hanging requests when the `api.get_data` is terminated by the async loop.

#### Testing

Tests can be run with PyTest and will test both the FastAPI endpoint and the `api.get_data` function. The tests are reliable as the endpoint is mocked, in order the remove the randomness of the external API.

## Services
These are the services launched by docker compose
#### Zipkin
Service used to collect telemetry and analyze the performance of the system. As the telemetry is served through OpenTelemetry, this can easily be swapped out with another service, like Jaeger or Prometheus.
#### Locust
This service can be used to stress test the application. The task is configured in `locustfile.py`, where each request will be launched with a random timeout between `500` and `1000` milliseconds. The outcome of the test can be then seen from the Zipkin Web UI.

Keep in mind that while Zipkin can be used to filter by response status code (and see how the exponea endpoint is behaving), Locust will show the test as successful if the response code is 200 and the timeout is respected, or if the code is 503, as it means that the exponea endpoint failed, but `/api/smart` behaved as expected.
#### Server
The `/api/smart` endpoint is served through a FastApi application, using uvicorn as a Gateway Interface.

The server requires Zipkin to be available (as you can see from `docker-compose.yml`).

## Improvements
- Exponea endpoint monitoring: currently, there isn't a way to easily understand how the external endpoint is behaving. Logs can be used for this, but having a dedicated metric for timeouts/service error/service unavailable/success would help with understanding what is going on behind the scenes.
- Response returns generic error: following what has been said in the previous point, the response returned by the local server doesn't give the reason for failure, but it only tells that the external endpoint was unreachable. Having a specific error for this would improve usability.
- Zipkin is currently required to be online when launching the server, this could be dynamically configured instead.
- There is no server protection at the moment. Possible improvement might involve using CloudFlare (for DDos protection), load shedding and rate limiting.
- To improve performances, multiple uvicorn workers might be used. At a higher level, a load balancer could be used to support multiple instances of the `server` service.