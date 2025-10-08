import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse

from mtgapi.config.settings.api import VERSION, APIConfiguration
from mtgapi.config.settings.defaults import KNOWN_ID_EXCEPTIONS
from mtgapi.config.wiring import wire_services
from mtgapi.domain.card import MTGCard
from mtgapi.services.apis.mtgio import MTGIOAPIService
from mtgapi.services.cache import cache_card_data, retrieve_card_data_from_cache

logger = logging.getLogger(__name__)


@asynccontextmanager
async def mtgio_api_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config: APIConfiguration
    with APIConfiguration().use() as config:
        logging.basicConfig(
            level=config.logging.level, format=config.logging.message_format, datefmt=config.logging.date_format
        )
        services_container = wire_services()
        services_container.init_resources()
        app.root_path = config.root_path
        try:
            yield
        finally:
            services_container.shutdown_resources()


API = FastAPI(
    title="MTG API",
    version=VERSION,
    lifespan=mtgio_api_lifespan,
)


@API.get("/card/{card_identifier}")
async def get_card(
    card_identifier: str, mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)]
) -> MTGCard:
    if card_identifier in KNOWN_ID_EXCEPTIONS:
        exception_reason = KNOWN_ID_EXCEPTIONS[card_identifier]
        logger.warning("Card identifier '%s' is in known exceptions: %s", card_identifier, exception_reason)
        raise HTTPException(status_code=400, detail=exception_reason)

    if not card_identifier.isdigit():
        raise ValueError("Card identifier must be an integer.")

    cached_entry: MTGCard = await retrieve_card_data_from_cache(card_identifier)
    if cached_entry:
        return cached_entry
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


@API.get("/metrics", tags=["_internal"], summary="Metrics (placeholder)")
async def metrics_placeholder() -> JSONResponse:  # pragma: no cover - placeholder
    """
    Placeholder metrics endpoint.

    Returns 501 until metrics collection (Prometheus / OTEL) is implemented.
    """
    return JSONResponse(status_code=501, content={"detail": "metrics not implemented"})


@API.get("/_trace/test", tags=["_internal"], summary="Tracing probe (placeholder)")
async def tracing_probe_placeholder() -> JSONResponse:  # pragma: no cover - placeholder
    """
    Placeholder trace test endpoint.

    Will emit a span once tracing is wired. Useful for validating exporter config.
    """
    return JSONResponse(status_code=501, content={"detail": "tracing not implemented"})


@API.get("/feature-flags", tags=["_internal"], summary="Feature flags (placeholder)")
async def feature_flags_placeholder() -> JSONResponse:  # pragma: no cover - placeholder
    """
    Placeholder feature flags listing.

    Future: integrate with a flag provider (e.g. LaunchDarkly, config file) and surface active flags.
    """
    return JSONResponse(status_code=501, content={"flags": {}, "detail": "feature flags not implemented"})
