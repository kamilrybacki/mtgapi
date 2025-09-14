import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, FastAPI, Response

from mtgcobuilderapi.config.settings.api import VERSION, APIConfiguration
from mtgcobuilderapi.config.wiring import wire_services
from mtgcobuilderapi.domain.card import MTGCard
from mtgcobuilderapi.services.apis.mtgio import MTGIOAPIService
from mtgcobuilderapi.services.cache import retrieve_card_data_from_cache


async def mtgio_api_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config: APIConfiguration
    with APIConfiguration().use() as config:
        logging.basicConfig(
            level=config.logging.level, format=config.logging.message_format, datefmt=config.logging.date_format
        )
        services_container = wire_services()
        services_container.init_resources()
        app.root_path = config.root_path
        yield
        services_container.shutdown_resources()


API = FastAPI(
    title="MTGCobuilder API",
    version=VERSION,
    lifespan=mtgio_api_lifespan,  # type: ignore
)


@API.get("/card/{card_identifier}")
async def get_card(card_identifier: int | str, mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)]) -> MTGCard:
    if isinstance(card_identifier, str) and not card_identifier.isdigit():
        raise ValueError("Card identifier must be an integer.")
    card_identifier = int(card_identifier)
    cached_entry: MTGCard = await retrieve_card_data_from_cache(card_identifier)
    if cached_entry:
        return cached_entry
    card_data_from_mtgio = await mtgio_service.get_card(card_identifier)
    return MTGCard.from_mtgio_card(card_data_from_mtgio)


@API.get("/card/{card_identifier}/image")
async def get_card_image(card_identifier: int, mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)]) -> Response:
    card_data_from_mtgio = await get_card(card_identifier, mtgio_service)
    return Response(content=await mtgio_service.get_card_image(card_data_from_mtgio), media_type="image/webp")
