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
        results = await database.get_objects(object_type=MTGCard, filters={"multiverse_id": identifier})
        if not results:
            logging.info(f"[CACHE] No data for id={identifier} present in cache")
            return MTGCard.null()  # type: ignore
    except Exception as encountered_exception:
        logging.exception("[CACHE] Failed to retrieve cached card data", exc_info=encountered_exception)
        return MTGCard.null()  # type: ignore

    data = results[0]
    logging.info(f"[CACHE] Retrieved cached data for id={identifier}: {data.name}")
    return MTGCard(**data.__dict__)


@inject
async def cache_card_data(
    card: MTGCard, database: PostgresDatabaseService = Provide[AuxiliaryServiceNames.DATABASE]
) -> None:
    """
    Cache card data.

    :param card:
        The card data to cache.
    :param database:
        The database service to use for caching the card data.
    :return:
        True if the card data was successfully cached, otherwise False.
    """
    await database.register(model=MTGCard)
    try:
        insertion_result = await database.insert(instance=card)
        if not insertion_result:
            logging.error(f"[CACHE] Failed to cache card data for id={card.id}")
    except Exception as encountered_exception:
        logging.exception("[CACHE] Failed to cache card data", exc_info=encountered_exception)
    else:
        logging.info(f"[CACHE] Cached card data for id={card.id}")
