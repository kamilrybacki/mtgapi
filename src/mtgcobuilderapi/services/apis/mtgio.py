import dataclasses
import logging
import re
import urllib.parse

import httpx

from mtgcobuilderapi.config.settings.services import MTGIOAPIConfiguration
from mtgcobuilderapi.domain.card import MTGCard, MTGIOCard
from mtgcobuilderapi.services.http import AbstractAsyncHTTPClientService


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

    async def get_card(self, identifier: str | int, raw: bool = False) -> MTGIOCard:
        """
        Fetches a card by its identifier (name or ID) from the MTGIO API.
        """
        fetch_by_name = isinstance(identifier, str) and not identifier.isdigit()
        url_query_part = "?name=" if fetch_by_name else "/"

        if fetch_by_name:
            identifier = (
                f'"{urllib.parse.quote_plus(str(identifier))}"'
                if all(c.isalnum() or c.isspace() for c in str(identifier))
                else identifier
            )

        raw_url = f"/{self.version}/{MTGIOAPIConfiguration.APIEndpoints.CARDS}{url_query_part}{identifier}"
        response = await self.get(raw_url)
        response.raise_for_status()
        payload = response.json()
        found_card_data = payload.get("cards", [{}])[0] if fetch_by_name else payload.get("card", {})
        card_name = found_card_data.get("name", "")

        if not card_name:
            raise ValueError(f"Card with identifier '{identifier}' not found or has no name.")

        logging.info(f"[INFO] Found card [[{card_name}]] on MTGIO API.")
        logging.debug(found_card_data)

        return MTGIOCard.from_api_payload(found_card_data) if not raw else found_card_data

    async def get_card_image(self, card: MTGCard) -> bytes | None:
        """
        Fetches the image of a card from the MTGIO API.
        """
        if not card.image_url:
            logging.warning(f"[WARNING] Card [[{card.name}]] has no image URL.")
            return None

        try:
            response = await self.get(url=card.image_url, override_base=True)
            response.raise_for_status()
        except httpx.HTTPStatusError as card_image_retrieval_error:
            logging.exception(
                f"[ERROR] Failed to fetch image for card [[{card.name}]]", exc_info=card_image_retrieval_error
            )
            return None
        else:
            return response.content
