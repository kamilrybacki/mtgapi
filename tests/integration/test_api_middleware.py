import logging

from mtgapi.config.wiring import wire_services
from mtgapi.services import AuxiliaryServiceNames
import pytest

from mtgapi.services.cache import retrieve_card_data_from_cache
from mtgapi.domain.card import MTGCard
from mtgapi.services.database import PostgresDatabaseService
from tests.common.helpers import use_postgres_container
from tests.common.samples import LIGHTNING_BOLT_MTG_CARD_DATA


@pytest.mark.asyncio
@pytest.mark.offline
@pytest.mark.chosen
async def test_getting_existing_cache_entry() -> None:
    with use_postgres_container():
        services = wire_services()
        postgres_service: PostgresDatabaseService = getattr(services, AuxiliaryServiceNames.DATABASE)()
        target_card_id = LIGHTNING_BOLT_MTG_CARD_DATA.get("multiverse_id")
        if target_card_id is None:
            raise ValueError("Test data must have a 'multiverse_id' field. Check test samples.")

        logging.info("[TEST] Testing getting non-existing cache entry")
        null_cache_entry = await retrieve_card_data_from_cache(target_card_id)  # type: ignore
        assert null_cache_entry is None

        instance_to_insert = MTGCard(**LIGHTNING_BOLT_MTG_CARD_DATA)  # type: ignore

        logging.info(f"[TEST] Inserting instance into database: {instance_to_insert}")
        await postgres_service.insert(instance_to_insert)

        cached_entry = await retrieve_card_data_from_cache(target_card_id)
        assert cached_entry is not None

        logging.info(f"[TEST] Retrieved cached entry: {cached_entry}")
        assert cached_entry.multiverse_id == target_card_id
        assert instance_to_insert == cached_entry
