import io
import logging
from urllib.parse import quote

import imagehash
import pytest
from PIL import Image
from httpx import AsyncClient

from mtgapi.config.settings.api import APIConfiguration
from mtgapi.domain.card import MTGCard, MTGIOCard
from mtgapi.services.apis.mtgio import MTGIOAPIService
from tests.common.helpers import generate_random_card_ids
from tests.common.samples import TEST_MTGIO_CARD_ID, TEST_MTGIO_CARD_IMAGE


@pytest.mark.asyncio
@pytest.mark.parametrize("target_id", generate_random_card_ids(10))  # Example target IDs
async def test_getting_card_data(
    test_cobuilder_api_client: AsyncClient, test_mtgio_service: MTGIOAPIService, target_id: int
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
async def test_getting_card_data_by_name(
    test_cobuilder_api_client: AsyncClient, test_mtgio_service: MTGIOAPIService
) -> None:
    mtgio_card = await test_mtgio_service.get_card(TEST_MTGIO_CARD_ID)
    processed_card_data = MTGCard.from_mtgio_card(mtgio_card)
    card_name = processed_card_data.name
    requested_printing = processed_card_data.set_name or ""

    response = await test_cobuilder_api_client.get(
        f"/card/{quote(card_name, safe='')}",
        params={"printing": requested_printing} if requested_printing else None,
    )
    assert response.status_code == 200

    card_from_api_response = MTGCard(**response.json())
    mtgio_card_by_name = await test_mtgio_service.get_card(card_name, printing=requested_printing or None)
    processed_card_data_from_name = MTGCard.from_mtgio_card(mtgio_card_by_name)

    assert card_from_api_response
    assert card_from_api_response.name == processed_card_data_from_name.name
    assert card_from_api_response.set_name == processed_card_data_from_name.set_name
    assert card_from_api_response.text == processed_card_data_from_name.text
    assert card_from_api_response.types == processed_card_data_from_name.types


@pytest.mark.asyncio
async def test_getting_card_data_by_id_and_name(
    test_cobuilder_api_client: AsyncClient, test_mtgio_service: MTGIOAPIService
) -> None:
    mtgio_card_by_id = await test_mtgio_service.get_card(TEST_MTGIO_CARD_ID)
    processed_card_by_id = MTGCard.from_mtgio_card(mtgio_card_by_id)
    requested_printing = processed_card_by_id.set_name or ""

    response_by_id = await test_cobuilder_api_client.get(f"/card/{TEST_MTGIO_CARD_ID}")
    response_by_name = await test_cobuilder_api_client.get(
        f"/card/{quote(processed_card_by_id.name, safe='')}",
        params={"printing": requested_printing} if requested_printing else None,
    )

    assert response_by_id.status_code == 200
    assert response_by_name.status_code == 200

    card_from_id_lookup = MTGCard(**response_by_id.json())
    card_from_name_lookup = MTGCard(**response_by_name.json())

    mtgio_card_by_name = await test_mtgio_service.get_card(
        processed_card_by_id.name, printing=requested_printing or None
    )
    processed_card_by_name = MTGCard.from_mtgio_card(mtgio_card_by_name)

    assert card_from_id_lookup.name == processed_card_by_id.name
    assert card_from_id_lookup.set_name == processed_card_by_id.set_name
    assert card_from_name_lookup.name == processed_card_by_name.name
    assert card_from_name_lookup.set_name == processed_card_by_name.set_name
    assert card_from_id_lookup.name == card_from_name_lookup.name
    assert card_from_id_lookup.set_name == card_from_name_lookup.set_name
    assert card_from_id_lookup.text == card_from_name_lookup.text
    assert card_from_id_lookup.types == card_from_name_lookup.types


@pytest.mark.asyncio
async def test_getting_card_data_by_name_with_invalid_printing(
    test_cobuilder_api_client: AsyncClient, test_mtgio_service: MTGIOAPIService
) -> None:
    mtgio_card = await test_mtgio_service.get_card(TEST_MTGIO_CARD_ID)
    processed_card = MTGCard.from_mtgio_card(mtgio_card)

    response = await test_cobuilder_api_client.get(
        f"/card/{quote(processed_card.name, safe='')}",
        params={"printing": "ZZZ"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_getting_card_image(test_cobuilder_api_client: AsyncClient, test_mtgio_service: MTGIOAPIService) -> None:
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
