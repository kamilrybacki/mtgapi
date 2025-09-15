import io
import random

import httpx
import imagehash
from mtgapi.domain.card import MTGCard
import pytest
import requests
from PIL import Image

from mtgapi.config.settings.defaults import MTGIO_API_VERSION, MTGIO_BASE_URL
from mtgapi.config.settings.services import MTGIOAPIConfiguration
from mtgapi.services.apis.mtgio import MTGIOAPIService
from tests.common.samples import TEST_MTGIO_CARD_ID, TEST_MTGIO_CARD_IMAGE

QUERY_TESTS_NUMBER = 10


@pytest.mark.parametrize(
    "target_id",
    [random.choice(range(100, 1000)) for _ in range(QUERY_TESTS_NUMBER)],
)
@pytest.mark.asyncio
async def test_querying_for_a_card(
    target_id: int,
    test_mtgio_service: MTGIOAPIService,
) -> None:
    full_cards_endpoint_url = (
        f"{MTGIO_BASE_URL}/{MTGIO_API_VERSION}/{MTGIOAPIConfiguration.APIEndpoints.CARDS}/{target_id}"
    )
    real_data_for_card = requests.get(
        full_cards_endpoint_url,
        headers={"Accept": "application/json"},
    ).json()
    assert isinstance(real_data_for_card, dict), "Expected a dictionary response for the card data"

    target_card_name = real_data_for_card.get("card", {}).get("name", "")
    assert target_card_name, "Fetched card name should not be empty"

    query_by_id_result = await test_mtgio_service.get_card(target_id)
    query_by_name_result = await test_mtgio_service.get_card(target_card_name)

    assert query_by_id_result, "Query by ID should return a result"
    assert query_by_name_result, "Query by name should return a result"

    assert query_by_id_result == query_by_name_result, "Results from ID and name queries should match"


@pytest.mark.asyncio
async def test_querying_for_a_card_with_invalid_id(
    test_mtgio_service: MTGIOAPIService,
) -> None:
    invalid_id = -1  # An ID that is unlikely to exist
    with pytest.raises(httpx.HTTPStatusError, match="404 Not Found"):
        await test_mtgio_service.get_card(invalid_id)


@pytest.mark.asyncio
async def test_getting_card_image(
    test_mtgio_service: MTGIOAPIService,
) -> None:
    plains_mtgio_card = await test_mtgio_service.get_card(TEST_MTGIO_CARD_ID)
    assert plains_mtgio_card, "Expected to fetch a valid card"

    plains_mtg_card = MTGCard.from_mtgio_card(plains_mtgio_card)
    assert plains_mtg_card.image_url, "Card should have an image URL"

    image_data = await test_mtgio_service.get_card_image(plains_mtg_card)
    assert image_data, "Expected to fetch card image data"
    assert isinstance(image_data, bytes), "Card image data should be in bytes format"

    assert len(image_data) > 0, "Card image data should not be empty"

    downloaded_image_memory_buffer = io.BytesIO()
    Image.open(io.BytesIO(image_data)).convert("RGB").save(downloaded_image_memory_buffer, format="png")

    reference_image_memory_buffer = io.BytesIO()
    TEST_MTGIO_CARD_IMAGE.convert("RGB").save(reference_image_memory_buffer, format="png")

    assert imagehash.average_hash(Image.open(downloaded_image_memory_buffer)) == imagehash.average_hash(
        Image.open(reference_image_memory_buffer)
    ), "Downloaded card image should match the reference image"
