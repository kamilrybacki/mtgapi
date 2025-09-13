import pytest

from tests.common.services import TEST_HTTP_SERVICE_BASE_URL, PokeAPIClientService, ThreeProxyService


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    ["pokemon/ditto", "pokemon-species/aegislash", "type/3", "ability/battle-armor", "pokemon?limit=100000&offset=0"],
)
async def test_http_service_initialization(pokeapi_service: PokeAPIClientService, endpoint: str) -> None:
    """
    Test the initialization of the HTTP service.
    """
    assert pokeapi_service.base_url == TEST_HTTP_SERVICE_BASE_URL, "Base URL should be set correctly."

    # Test a simple GET request
    response = await pokeapi_service.get(endpoint)
    assert response.status_code == 200, "Expected status code 200 for health check."
    assert response.json(), "Expected health check response to be non-empty."

    await pokeapi_service.disconnect()


@pytest.mark.asyncio
async def test_proxy_service_initialization(
    three_proxy_service: ThreeProxyService,
    pokeapi_service: PokeAPIClientService,
) -> None:
    """
    Test the initialization of the proxy service.
    """
    pokeapi_service._proxy_provider = three_proxy_service

    response = await pokeapi_service.get("pokemon/ditto")
    assert response.status_code == 200, "Expected status code 200 for proxy service health check."
    assert response.json(), "Expected proxy service health check response to be non-empty."
