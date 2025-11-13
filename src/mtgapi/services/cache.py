import logging

from dependency_injector.wiring import Provide, inject

from mtgapi.domain.card import MTGCard
from mtgapi.services import AuxiliaryServiceNames
from mtgapi.services.database import PostgresDatabaseService

logger = logging.getLogger(__name__)


@inject
async def retrieve_card_data_from_cache(
    identifier: str,
    printing: str | None = None,
    database: PostgresDatabaseService = Provide[AuxiliaryServiceNames.DATABASE],
) -> MTGCard:
    """
    Retrieve card data from the cache.

    :param identifier:
        The identifier of the card to retrieve. Accepts a multiverse ID or a card name.
    :param printing:
        Optional set code for the desired printing. Only applied for name-based lookups.
    :param database:
        The database service to use for retrieving the card data.
    :return:
        The card data if found in the cache, otherwise None.
    """
    await database.register(model=MTGCard)
    try:
        normalized_identifier = identifier.strip()
        normalized_printing = printing.strip().upper() if isinstance(printing, str) and printing.strip() else None
        if normalized_identifier.isdigit():
            lookup_filters = {"multiverse_id": normalized_identifier}
        else:
            lookup_filters = {"name": normalized_identifier}

        if normalized_printing:
            lookup_filters["set_name"] = normalized_printing
        results = await database.get_objects(object_type=MTGCard, filters=lookup_filters)
        if not results:
            logger.info("No data for id=%s present in cache", identifier)
            return MTGCard.null()
    except Exception as encountered_exception:
        logger.exception("Failed to retrieve cached card data", exc_info=encountered_exception)
        return MTGCard.null()

    data: MTGCard = results[0]
    logger.info("Retrieved cached data for id=%s: %s", identifier, data.name)
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
            logger.error("Failed to cache card data for id=%s", card.id)
    except Exception as encountered_exception:
        logger.exception("Failed to cache card data", exc_info=encountered_exception)
    else:
        logger.info("Cached card data for id=%s", card.id)
