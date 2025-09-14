import io
import logging

import imagehash
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from mtgcobuilderapi.config.settings.api import APIConfiguration
from mtgcobuilderapi.domain.card import MTGCard, MTGIOCard
from mtgcobuilderapi.services.apis.mtgio import MTGIOAPIService
from tests.common.helpers import generate_random_card_ids
from tests.common.samples import TEST_MTGIO_CARD_ID, TEST_MTGIO_CARD_IMAGE


@pytest.mark.asyncio
@pytest.mark.parametrize("target_id", generate_random_card_ids(10))  # Example target IDs
async def test_getting_card_data(
    test_cobuilder_api_client: TestClient, test_mtgio_service: MTGIOAPIService, target_id: int
) -> None:
    with APIConfiguration.use() as config:
        logging.info(f"[TEST] Getting card data for {target_id}")
        response = await test_cobuilder_api_client.get(
            f"/card/{target_id}",
        )
        assert response.status_code == 200
        card_from_api_response: MTGCard = MTGCard(**response.json())

        card_data_from_mtgio: MTGIOCard = await test_mtgio_service.get_card(target_id)
        processed_card_data = MTGCard.from_mtgio_card(card_data_from_mtgio)

        assert card_from_api_response == processed_card_data, (
            f"Expected card data to match processed MTGIOCard, "
            f"but got {card_from_api_response} instead of {processed_card_data}"
        )


@pytest.mark.asyncio
async def test_getting_card_image(test_cobuilder_api_client: TestClient, test_mtgio_service: MTGIOAPIService) -> None:
    with APIConfiguration.use() as config:
        logging.info("[TEST] Getting card image")
        response = await test_cobuilder_api_client.get(
            f"/card/{TEST_MTGIO_CARD_ID}/image",
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "image/webp"
        assert len(response.content) > 0, "Expected non-empty image content"

        downloaded_image_memory_buffer = io.BytesIO()
        Image.open(io.BytesIO(response.content)).convert("RGB").save(downloaded_image_memory_buffer, format="png")

        reference_image_memory_buffer = io.BytesIO()
        TEST_MTGIO_CARD_IMAGE.convert("RGB").save(reference_image_memory_buffer, format="png")

        assert imagehash.average_hash(Image.open(downloaded_image_memory_buffer)) == imagehash.average_hash(
            Image.open(reference_image_memory_buffer)
        ), "Downloaded card image should match the reference image"
