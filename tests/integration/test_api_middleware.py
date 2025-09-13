import logging

import pytest

from mtgcobuilderapi.api.middleware.cache import retrieve_card_data_from_cache
from mtgcobuilderapi.domain.card import MTGCard
from mtgcobuilderapi.services.database import PostgresDatabaseService
from tests.common.helpers import use_postgres_container
from tests.common.samples import LIGHTNING_BOLT_MTG_CARD_DATA


@pytest.mark.asyncio
@pytest.mark.chosen
@pytest.mark.offline
async def test_getting_existing_cache_entry() -> None:
    with use_postgres_container():
        postgres_service = PostgresDatabaseService()
        target_card_id = LIGHTNING_BOLT_MTG_CARD_DATA.get("id")
        if target_card_id is None:
            raise ValueError("Test data must have an 'id' field. Check test samples.")

        logging.info("[TEST] Testing getting non-existing cache entry")
        null_cache_entry = await retrieve_card_data_from_cache(target_card_id)  # type: ignore
        assert null_cache_entry is None

        instance_to_insert = MTGCard(**LIGHTNING_BOLT_MTG_CARD_DATA)  # type: ignore

        logging.info(f"[TEST] Inserting instance into database: {instance_to_insert}")
        await postgres_service.insert(instance_to_insert)

        cached_entry = await retrieve_card_data_from_cache(target_card_id)
        assert cached_entry is not None

        logging.info(f"[TEST] Retrieved cached entry: {cached_entry}")
        assert cached_entry.id == target_card_id
        assert instance_to_insert == cached_entry
