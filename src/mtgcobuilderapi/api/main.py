from fastapi import FastAPI, Response

from dependency_injector.wiring import Provide, inject
from mtgcobuilderapi.config.settings.api import APIConfiguration, VERSION
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


@API.get("/card/{id}", response_model=MTGCard)
async def get_card(id: int | str) -> MTGCard:
    card_data_from_mtgio = await use_mtgio_service().get_card(id)
    card_data = MTGCard.from_mtgio_card(card_data_from_mtgio)
    return card_data


@API.get("/card/{id}/image")
async def get_card_image(id: int) -> Response:
    card_data_from_mtgio = await get_card(id)
    return Response(content=await use_mtgio_service().get_card_image(card_data_from_mtgio), media_type="image/webp")
