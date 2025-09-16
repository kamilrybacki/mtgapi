import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, FastAPI, Response, HTTPException

from mtgapi.config.settings.api import VERSION, APIConfiguration
from mtgapi.config.settings.defaults import KNOWN_ID_EXCEPTIONS
from mtgapi.config.wiring import wire_services
from mtgapi.domain.card import MTGCard
from mtgapi.services.apis.mtgio import MTGIOAPIService
from mtgapi.services.cache import cache_card_data, retrieve_card_data_from_cache


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
async def get_card(
    card_identifier: str, mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)]
) -> MTGCard:
    if card_identifier in KNOWN_ID_EXCEPTIONS:
        exception_reason = KNOWN_ID_EXCEPTIONS[card_identifier]
        logging.warning(f"Card identifier '{card_identifier}' is in known exceptions: {exception_reason}")
        raise HTTPException(status_code=400, detail=exception_reason)

    if not card_identifier.isdigit():
        raise ValueError("Card identifier must be an integer.")

    cached_entry: MTGCard = await retrieve_card_data_from_cache(card_identifier)
    if cached_entry:
        return cached_entry
    else:
        card_data_from_mtgio = await mtgio_service.get_card(int(card_identifier))
        mtg_card = MTGCard.from_mtgio_card(card_data_from_mtgio)
        await cache_card_data(mtg_card)
        return mtg_card


@API.get("/card/{card_identifier}/image")
async def get_card_image(
    card_identifier: str, mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)]
) -> Response:
    card_data_from_mtgio = await get_card(card_identifier, mtgio_service)
    return Response(content=await mtgio_service.get_card_image(card_data_from_mtgio), media_type="image/webp")
