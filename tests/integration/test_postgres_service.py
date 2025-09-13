import pytest

from mtgcobuilderapi.services.database import PostgresDatabaseService
from tests.common.helpers import use_postgres_container


@pytest.mark.asyncio
@pytest.mark.offline
async def test_postgres_service_initialization() -> None:
    with use_postgres_container():
        postgres_service = PostgresDatabaseService()

        assert postgres_service.client is not None, "Postgres service client should be initialized."
        assert postgres_service.session is not None, "Postgres service session should be initialized."

        # Test connection by executing a simple query
        result = await postgres_service.query("SELECT 1")
        assert result == [(1,)], "Expected result from the query to be [(1,)]"
        await postgres_service.disconnect()
