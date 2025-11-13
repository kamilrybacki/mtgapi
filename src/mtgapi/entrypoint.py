import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError

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
    card_identifier: str,
    mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)],
    printing: Annotated[
        str | None,
        Query(
            description="Optional MTG set code (printing) to disambiguate cards that share a name.",
            min_length=1,
            max_length=10,
        ),
    ] = None,
) -> MTGCard:
    normalized_identifier = card_identifier.strip()
    normalized_printing = printing.strip().upper() if isinstance(printing, str) and printing.strip() else None

    if not normalized_identifier:
        raise HTTPException(status_code=400, detail="Card identifier must not be empty.")

    if normalized_identifier in KNOWN_ID_EXCEPTIONS:
        exception_reason = KNOWN_ID_EXCEPTIONS[normalized_identifier]
        logger.warning("Card identifier '%s' is in known exceptions: %s", card_identifier, exception_reason)
        raise HTTPException(status_code=400, detail=exception_reason)

    cached_entry: MTGCard = await retrieve_card_data_from_cache(normalized_identifier, normalized_printing)
    if cached_entry and (not normalized_printing or cached_entry.set_name == normalized_printing):
        return cached_entry

    identifier_for_lookup: int | str = (
        int(normalized_identifier) if normalized_identifier.isdigit() else normalized_identifier
    )

    try:
        card_data_from_mtgio = await mtgio_service.get_card(identifier_for_lookup, printing=normalized_printing)
    except HTTPStatusError as http_error:
        try:
            error_payload = http_error.response.json()
            detail = error_payload.get("error") if isinstance(error_payload, dict) else error_payload
        except ValueError:
            detail = http_error.response.text or "Failed to retrieve card data from upstream service."
        raise HTTPException(status_code=http_error.response.status_code, detail=detail) from http_error
    except ValueError as card_not_found_error:
        raise HTTPException(status_code=404, detail=str(card_not_found_error)) from card_not_found_error

    mtg_card = MTGCard.from_mtgio_card(card_data_from_mtgio)
    if normalized_printing and mtg_card.set_name != normalized_printing:
        raise HTTPException(
            status_code=404,
            detail=f"Card found but printing '{mtg_card.set_name}' does not match requested '{normalized_printing}'.",
        )
    await cache_card_data(mtg_card)
    return mtg_card


@API.get("/card/{card_identifier}/image")
async def get_card_image(
    card_identifier: str,
    mtgio_service: Annotated[MTGIOAPIService, Depends(MTGIOAPIService)],
    printing: Annotated[
        str | None,
        Query(
            description="Optional MTG set code (printing) to disambiguate cards that share a name.",
            min_length=1,
            max_length=10,
        ),
    ] = None,
) -> Response:
    card_data_from_mtgio = await get_card(card_identifier, mtgio_service, printing)
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
