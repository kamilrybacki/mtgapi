from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Response

from mtgcobuilderapi.config.settings.api import VERSION, APIConfiguration
from mtgcobuilderapi.domain.card import MTGCard
from mtgcobuilderapi.services import InjectedServiceNames
from mtgcobuilderapi.services.apis.mtgio import MTGIOAPIService

with APIConfiguration.use() as configuration:
    API = FastAPI(
        title="MTGCobuilder API",
        root_path=configuration.root_path,  # type: ignore
        version=VERSION,
    )


@inject
def use_mtgio_service(mtgio: MTGIOAPIService = Provide[InjectedServiceNames.MTGIO]) -> MTGIOAPIService:
    return mtgio


@API.get("/card/{card_identifier}")
async def get_card(card_identifier: int | str) -> MTGCard:
    card_data_from_mtgio = await use_mtgio_service().get_card(card_identifier)
    return MTGCard.from_mtgio_card(card_data_from_mtgio)


@API.get("/card/{card_identifier}/image")
async def get_card_image(card_identifier: int) -> Response:
    card_data_from_mtgio = await get_card(card_identifier)
    return Response(content=await use_mtgio_service().get_card_image(card_data_from_mtgio), media_type="image/webp")
