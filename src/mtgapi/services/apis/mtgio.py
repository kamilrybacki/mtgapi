import dataclasses
import logging
import re
import urllib.parse

import httpx

from mtgapi.config.settings.services import MTGIOAPIConfiguration
from mtgapi.domain.card import MTGCard, MTGIOCard
from mtgapi.services.http import AbstractAsyncHTTPClientService

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MTGIOAPIService(AbstractAsyncHTTPClientService, config=MTGIOAPIConfiguration):
    limit_header: str = dataclasses.field(init=False)
    version: str = dataclasses.field(init=False)

    def _post_init(self, config: MTGIOAPIConfiguration) -> None:  # type: ignore
        self.limit_header = config.rate_limit_header
        self.version = config.version

    def construct_auth(self, config: MTGIOAPIConfiguration) -> httpx.Auth | None:  # type: ignore  # noqa: ARG002
        return None

    def construct_headers(self, config: MTGIOAPIConfiguration) -> dict[str, str]:  # type: ignore  # noqa: ARG002
        return {}

    def check_rate_limit(self, response: httpx.Response) -> bool:
        return int(response.headers.get(self.limit_header, 0)) > 0

    @staticmethod
    def convert_payload_key(key: str) -> str:
        """
        Converts payload keys to match the MTGIOCard dataclass field names.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

    async def get_card(self, identifier: str | int, printing: str | None = None, raw: bool = False) -> MTGIOCard:
        """
        Fetches a card by its identifier (name or ID) from the MTGIO API.

        :param identifier:
            The card name or multiverse ID used for lookup.
        :param printing:
            Optional set code (e.g. "10E") to restrict name-based lookups to a specific printing.
        :param raw:
            When True, return the raw MTGIO payload instead of an MTGIOCard model.
        """
        fetch_by_name = isinstance(identifier, str) and not identifier.isdigit()
        normalized_printing = printing.strip().upper() if isinstance(printing, str) and printing.strip() else None

        if fetch_by_name:
            name_value = str(identifier)
            quoted_name = f'"{name_value}"' if all(c.isalnum() or c.isspace() for c in name_value) else name_value
            query_params = {"name": quoted_name}
            if normalized_printing:
                query_params["set"] = normalized_printing
            raw_url = (
                f"/{self.version}/{MTGIOAPIConfiguration.APIEndpoints.CARDS}?"
                f"{urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote_plus)}"
            )
        else:
            raw_url = f"/{self.version}/{MTGIOAPIConfiguration.APIEndpoints.CARDS}/{identifier}"

        response = await self.get(raw_url)
        response.raise_for_status()
        payload = response.json()

        if fetch_by_name:
            cards_payload = payload.get("cards", [])
            if not isinstance(cards_payload, list) or not cards_payload:
                raise ValueError(
                    f"Card with name '{identifier}' and printing '{normalized_printing or 'ANY'}' not found."
                )

            if normalized_printing:
                cards_payload = [card for card in cards_payload if card.get("set", "").upper() == normalized_printing]
                if not cards_payload:
                    raise ValueError(f"Card with name '{identifier}' and printing '{normalized_printing}' not found.")

            found_card_data = cards_payload[0]
        else:
            found_card_data = payload.get("card", {})
            if not found_card_data:
                raise ValueError(f"Card with identifier '{identifier}' not found.")
        card_name = found_card_data.get("name", "")

        if not card_name:
            raise ValueError(f"Card with identifier '{identifier}' not found or has no name.")

        logger.info("Found card [[%s]] on MTGIO API.", card_name)
        logger.debug(found_card_data)

        return MTGIOCard.from_api_payload(found_card_data) if not raw else found_card_data

    async def get_card_image(self, card: MTGCard) -> bytes | None:
        """
        Fetches the image of a card from the MTGIO API.
        """
        if not card.image_url:
            logger.warning("Card [[%s]] has no image URL.", card.name)
            return None

        try:
            response = await self.get(url=card.image_url, override_base=True)
            response.raise_for_status()
        except httpx.HTTPStatusError as card_image_retrieval_error:
            logger.exception("Failed to fetch image for card [[%s]]", card.name, exc_info=card_image_retrieval_error)
            return None
        else:
            return bytes(response.content)
