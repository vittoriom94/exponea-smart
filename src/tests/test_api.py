import httpx
import pytest

import api
import exceptions
import tests.utils


class TestApi:
    @pytest.mark.asyncio
    async def test_api_first_successful(self, httpx_mock):
        async with httpx.AsyncClient() as client:
            httpx_mock.add_response(json={"time": 100})
            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

    @pytest.mark.asyncio
    async def test_api_first_fail_second_successful(self, httpx_mock):
        async with httpx.AsyncClient() as client:
            httpx_mock.add_callback(tests.utils.unavailable_endpoint)
            httpx_mock.add_response(json={"time": 100})
            httpx_mock.add_response(json={"time": 100})

            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
            httpx_mock.add_response(json={"time": 100})
            httpx_mock.add_response(json={"time": 100})

            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

    @pytest.mark.asyncio
    async def test_api_only_one_works(self, httpx_mock):
        async with httpx.AsyncClient() as client:
            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
            httpx_mock.add_callback(tests.utils.unavailable_endpoint)
            httpx_mock.add_response(json={"time": 100})

            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
            httpx_mock.add_response(json={"time": 100})
            httpx_mock.add_callback(tests.utils.unavailable_endpoint)

            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
            httpx_mock.add_response(json={"time": 100})

            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
            httpx_mock.add_response(json={"time": 100})
            httpx_mock.add_exception(httpx.ReadTimeout("timeout"))

            result = await api.get_data(1000, client)
            assert isinstance(result["time"], int)

    @pytest.mark.asyncio
    async def test_api_all_errors(self, httpx_mock):
        async with httpx.AsyncClient() as client:
            with pytest.raises(exceptions.UnsuccessfulApiError):
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
                httpx_mock.add_callback(tests.utils.unavailable_endpoint)
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))

                await api.get_data(1000, client)

            with pytest.raises(exceptions.UnsuccessfulApiError):
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
                httpx_mock.add_callback(tests.utils.unavailable_endpoint)

                await api.get_data(1000, client)

            with pytest.raises(exceptions.UnsuccessfulApiError):
                httpx_mock.add_callback(tests.utils.unavailable_endpoint)
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))

                await api.get_data(1000, client)

            with pytest.raises(exceptions.UnsuccessfulApiError):
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))
                httpx_mock.add_exception(httpx.ReadTimeout("timeout"))

                await api.get_data(1000, client)

            with pytest.raises(exceptions.UnsuccessfulApiError):
                httpx_mock.add_callback(tests.utils.unavailable_endpoint)
                httpx_mock.add_callback(tests.utils.unavailable_endpoint)
                httpx_mock.add_callback(tests.utils.unavailable_endpoint)

                await api.get_data(1000, client)
