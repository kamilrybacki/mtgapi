import logging

from dependency_injector.wiring import Provide, inject

from mtgapi.domain.card import MTGCard
from mtgapi.services import AuxiliaryServiceNames
from mtgapi.services.database import PostgresDatabaseService


@inject
async def retrieve_card_data_from_cache(
    identifier: str, database: PostgresDatabaseService = Provide[AuxiliaryServiceNames.DATABASE]
) -> MTGCard:
    """
    Retrieve card data from the cache.

    :param identifier:
        The identifier of the card to retrieve - an integer representing the card ID.
    :param database:
        The database service to use for retrieving the card data.
    :return:
        The card data if found in the cache, otherwise None.
    """
    await database.register(model=MTGCard)
    try:
        results = await database.get_objects(object_type=MTGCard, filters={"id": identifier})
        if not results:
            logging.info(f"[CACHE] No data for id={identifier} present in cache")
            return MTGCard.null()  # type: ignore
    except Exception as encountered_exception:
        logging.exception("[CACHE] Failed to retrieve cached card data", exc_info=encountered_exception)
        return MTGCard.null()  # type: ignore

    data = results[0]
    return MTGCard(**data.__dict__)
