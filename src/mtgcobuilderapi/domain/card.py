import logging
import re
from enum import StrEnum
from typing import Any, TypedDict, ClassVar
from sqlalchemy.orm import declarative_base

from pydantic import BaseModel, Field, field_validator

PostgresEntriesBase = declarative_base()


class CharToManaColor(StrEnum):
    """Enumeration for mana colors represented by single characters."""

    W = "White"
    U = "Blue"
    B = "Black"
    R = "Red"
    G = "Green"
    C = "Colorless"
    X = "Generic"


CARD_POSSIBLE_LAYOUTS = [
    "normal",
    "split",
    "flip",
    "double-faced",
    "token",
    "plane",
    "scheme",
    "phenomenon",
    "leveler",
    "vanguard",
    "aftermath",
]


class ManaValue(BaseModel):
    """Represents the mana value of a Magic: The Gathering card."""

    generic: int | str = Field(default=0, description="Generic mana cost")
    colorless: int = Field(default=0, description="Colorless mana cost")
    white: int = Field(default=0, description="White mana cost")
    blue: int = Field(default=0, description="Blue mana cost")
    black: int = Field(default=0, description="Black mana cost")
    red: int = Field(default=0, description="Red mana cost")
    green: int = Field(default=0, description="Green mana cost")

    def total(self) -> int:
        """Calculate the total mana value."""
        return self.colorless + self.white + self.blue + self.black + self.red + self.green

    @classmethod
    def from_mtgio_cost_string(cls, cost_string: str) -> "ManaValue":
        """
        Create a ManaValue instance from a MTGIO cost string.
        The cost string is expected to be in the format '{COLORLESS as integer}{W/U/B/R/G}...'.
        """
        mana_value = cls()
        if not cost_string:
            return mana_value

        # Split the cost string into sections based on color and generic mana
        split_cost_string = cost_string.replace("{", "").replace("}", ",").split(",")
        for cost_section in split_cost_string:
            if not cost_section:
                continue

            mana_color_name = CharToManaColor.__members__.get(cost_section.upper())
            if mana_color_name == CharToManaColor.X:
                mana_value.generic = "X"
                continue

            if cost_section.isdigit():
                mana_value.generic = int(cost_section)
                continue

            if mana_color_name is None:
                raise ValueError(f"Invalid mana color: {cost_section} in cost string '{cost_string}'")

            current_color_value = getattr(mana_value, mana_color_name.value.lower(), 0)
            setattr(mana_value, mana_color_name.value.lower(), current_color_value + 1)

        return mana_value


class Keyword(StrEnum):
    """Enumeration for different types of counters that can be on a Magic: The Gathering card."""

    DEATHTOUCH = "Deathtouch"
    DEFENDER = "Defender"
    DOUBLE_STRIKE = "Double Strike"
    ENCHANT = "Enchant"
    EQUIP = "Equip"
    FIRST_STRIKE = "First Strike"
    FLASH = "Flash"
    FLYING = "Flying"
    HASTE = "Haste"
    HEXPROOF = "Hexproof"
    INDESTRUCTIBLE = "Indestructible"
    INTIMIDATE = "Intimidate"
    FORESTWALK = "Forestwalk"
    ISLANDWALK = "Islandwalk"
    MOUNTAINWALK = "Mountainwalk"
    PLAINSWALK = "Plainswalk"
    SWAMPWALK = "Swampwalk"
    LIFELINK = "Lifelink"
    PROTECTION = "Protection"
    REACH = "Reach"
    SHROUD = "Shroud"
    TRAMPLE = "Trample"
    VIGILANCE = "Vigilance"
    WARD = "Ward"
    BANDING = "Banding"
    RAMPAGE = "Rampage"
    CUMULATIVE_UPKEEP = "Cumulative Upkeep"
    FLANKING = "Flanking"
    PHASING = "Phasing"
    BUYBACK = "Buyback"
    SHADOW = "Shadow"
    CYCLING = "Cycling"
    ECHO = "Echo"
    HORSEMANSHIP = "Horsemanship"
    FADING = "Fading"
    KICKER = "Kicker"
    FLASHBACK = "Flashback"
    MADNESS = "Madness"
    FEAR = "Fear"
    MORPH = "Morph"
    AMPLIFY = "Amplify"
    PROVOKE = "Provoke"
    STORM = "Storm"
    AFFINITY = "Affinity"
    ENTWINE = "Entwine"
    MODULAR = "Modular"
    SUNBURST = "Sunburst"
    BUSHIDO = "Bushido"
    SOULSHIFT = "Soulshift"
    SPLICE = "Splice"
    OFFERING = "Offering"
    NINJUTSU = "Ninjutsu"
    EPIC = "Epic"
    CONVOKE = "Convoke"
    DREDGE = "Dredge"
    TRANSMUTE = "Transmute"
    BLOODTHIRST = "Bloodthirst"
    HAUNT = "Haunt"
    REPLICATE = "Replicate"
    FORECAST = "Forecast"
    GRAFT = "Graft"
    RECOVER = "Recover"
    RIPPLE = "Ripple"
    SPLIT_SECOND = "Split Second"
    SUSPEND = "Suspend"
    VANISHING = "Vanishing"
    ABSORB = "Absorb"
    AURA_SWAP = "Aura Swap"
    DELVE = "Delve"
    FORTIFY = "Fortify"
    FRENZY = "Frenzy"
    GRAVESTORM = "Gravestorm"
    POISONOUS = "Poisonous"
    TRANSFIGURE = "Transfigure"
    CHAMPION = "Champion"
    CHANGELING = "Changeling"
    EVOKE = "Evoke"
    HIDEAWAY = "Hideaway"
    PROWL = "Prowl"
    REINFORCE = "Reinforce"
    CONSPIRE = "Conspire"
    PERSIST = "Persist"
    WITHER = "Wither"
    RETRACE = "Retrace"
    DEVOUR = "Devour"
    EXALTED = "Exalted"
    UNEARTH = "Unearth"
    CASCADE = "Cascade"
    ANNIHILATOR = "Annihilator"
    LEVEL_UP = "Level Up"
    REBOUND = "Rebound"
    UMBRA_ARMOR = "Umbra Armor"
    INFECT = "Infect"
    BATTLE_CRY = "Battle Cry"
    LIVING_WEAPON = "Living Weapon"
    UNDYING = "Undying"
    MIRACLE = "Miracle"
    SOULBOND = "Soulbond"
    OVERLOAD = "Overload"
    SCAVENGE = "Scavenge"
    UNLEASH = "Unleash"
    CIPHER = "Cipher"
    EVOLVE = "Evolve"
    EXTORT = "Extort"
    FUSE = "Fuse"
    BESTOW = "Bestow"
    TRIBUTE = "Tribute"
    DETHRONE = "Dethrone"
    HIDDEN_AGENDA = "Hidden Agenda"
    OUTLAST = "Outlast"
    PROWESS = "Prowess"
    DASH = "Dash"
    EXPLOIT = "Exploit"
    MENACE = "Menace"
    RENOWN = "Renown"
    AWAKEN = "Awaken"
    DEVOID = "Devoid"
    INGEST = "Ingest"
    MYRIAD = "Myriad"
    SURGE = "Surge"
    SKULK = "Skulk"
    EMERGE = "Emerge"
    ESCALATE = "Escalate"
    MELEE = "Melee"
    CREW = "Crew"
    FABRICATE = "Fabricate"
    PARTNER = "Partner"
    UNDAUNTED = "Undaunted"
    IMPROVISE = "Improvise"
    AFTERMATH = "Aftermath"
    EMBALM = "Embalm"
    ETERNALIZE = "Eternalize"
    AFFLICT = "Afflict"
    ASCEND = "Ascend"
    ASSIST = "Assist"
    JUMP_START = "Jump-Start"
    MENTOR = "Mentor"
    AFTERLIFE = "Afterlife"
    RIOT = "Riot"
    SPECTACLE = "Spectacle"
    ESCAPE = "Escape"
    COMPANION = "Companion"
    MUTATE = "Mutate"
    ENCORE = "Encore"
    BOAST = "Boast"
    FORETELL = "Foretell"
    DEMONSTRATE = "Demonstrate"
    DAYBOUND_NIGHTBOUND = "Daybound and Nightbound"
    DISTURB = "Disturb"
    DECAYED = "Decayed"
    CLEAVE = "Cleave"
    TRAINING = "Training"
    COMPLEATED = "Compleated"
    RECONFIGURE = "Reconfigure"
    BLITZ = "Blitz"
    CASUALTY = "Casualty"
    ENLIST = "Enlist"
    READ_AHEAD = "Read Ahead"
    RAVENOUS = "Ravenous"
    SQUAD = "Squad"
    SPACE_SCULPTOR = "Space Sculptor"
    VISIT = "Visit"
    PROTOTYPE = "Prototype"
    LIVING_METAL = "Living Metal"
    MORE_THAN_MEETS_THE_EYE = "More Than Meets the Eye"
    FOR_MIRRODIN = "For Mirrodin!"
    TOXIC = "Toxic"
    BACKUP = "Backup"
    BARGAIN = "Bargain"
    CRAFT = "Craft"
    DISGUISE = "Disguise"
    SOLVED = "Solved"
    PLOT = "Plot"
    SADDLE = "Saddle"
    SPREE = "Spree"
    FREERUNNING = "Freerunning"
    GIFT = "Gift"
    OFFSPRING = "Offspring"
    IMPENDING = "Impending"
    EXHAUST = "Exhaust"
    MAX_SPEED = "Max Speed"
    START_YOUR_ENGINES = "Start Your Engines!"
    HARMONIZE = "Harmonize"
    MOBILIZE = "Mobilize"


class CardRarity(StrEnum):
    """Enumeration for card rarities."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    MYTHIC_RARE = "mythic"


class MTGCardAlias(TypedDict):
    """Represents a foreign name for a Magic: The Gathering card."""

    name: str
    language: str


class MTGCardRuling(TypedDict):
    """Represents a ruling for a Magic: The Gathering card."""

    date: str
    text: str


class MTGIOCard(BaseModel):
    """Represents a Magic: The Gathering card with additional fields for MTGIO."""

    MANA_COST_REGEX: ClassVar[str] = r"^(\{[0-9X]+\})*(\{[WUBRGC]\})*$"
    INVALID_MANA_COST_ERROR: ClassVar[str] = (
        "Invalid mana cost format: '{value}'. Expected format is '{{X}}({{C}}*)' where X is a number of colorless mana and C is a color pip character (W, U, B, R, G)."
    )

    names: list[str] = Field(
        default_factory=list,
        description="List of names the card can have",
        examples=[["Lightning Bolt"]],
    )
    mana_cost: str = Field(
        description="Mana cost of the card in {X}({C}*) format",
        examples=["{3}{W}{U}"],
    )
    colors: list[str] = Field(
        default_factory=list,
        description="List of colors the card belongs to",
        examples=[["Red"], ["Blue", "Red"]],
    )
    color_identity: list[str] = Field(
        default_factory=list,
        description="List of colors that define the card's identity (color codes, e.g. ['R', 'U'])",
        examples=[["R"], ["R", "U"]],
    )
    rarity: str = Field(
        default="common",
        description="Rarity of the card (e.g., common, uncommon, rare, mythic)",
        examples=["common", "uncommon", "rare", "mythic"],
        min_length=1,
        max_length=10,
    )
    types: list[str] = Field(
        default_factory=list,
        description="List of types the card belongs to (e.g. Creature, Instant, Sorcery, Artifact, Enchantment, Land, Planeswalker)",
        examples=[["Creature"], ["Instant"]],
        min_length=1,
    )
    subtypes: list[str] = Field(
        default_factory=list,
        description="List of subtypes the card belongs to (e.g. Human, Wizard, Squirrel)",
        examples=[["Human"], ["Rat", "Squirrel"]],
    )
    supertypes: list[str] = Field(
        default_factory=list,
        description="List of supertypes the card belongs to (e.g. Basic, Legendary, Snow, World, Ongoing)",
        examples=[["Legendary"]],
    )
    text: str | None = Field(
        None,
        description="Oracle text of the card. May contain mana symbols and other symbols.",
        examples=["Flying, Vigilance"],
    )
    flavor: str = Field(
        default="",
        description="Flavor text of the card, if any",
        examples=['"The storm is coming."'],
    )
    power: str | None = Field(
        None,
        description="Power of the creature card (e.g. '3', 'X')",
        examples=["3", "X"],
    )
    toughness: str | None = Field(
        None,
        description="Toughness of the creature card (e.g. '3', 'X')",
        examples=["3", "X"],
    )
    layout: str = Field(
        default="normal",
        description="Layout of the card (e.g., normal, split, flip, double-faced, token, plane, scheme, phenomenon, leveler, vanguard, aftermath)",
        examples=CARD_POSSIBLE_LAYOUTS,
        min_length=1,
        max_length=len(max(CARD_POSSIBLE_LAYOUTS, key=len) if CARD_POSSIBLE_LAYOUTS else 0),
    )
    rulings: list[MTGCardRuling] = Field(
        default_factory=list,
        description="List of rulings for the card",
    )
    foreign_names: list[MTGCardAlias] = Field(
        default_factory=list,
        description="List of foreign names for the card",
    )
    printings: list[str] = Field(
        default_factory=list,
        description="List of sets the card has been printed in",
        examples=[["LEA", "2ED"]],
    )
    id: str = Field(
        ...,
        description="Unique identifier for the card in the MTGIO database (SHA1 hash of setCode + cardName + cardImageName)",
        examples=["a1b2c3d4e5f6g7h8i9j0"],
    )
    image_url: str = Field(
        description="URL to the card's image in the MTGIO database",
        examples=["http://example.com/image.jpg"],
    )

    @classmethod
    def from_api_payload(cls, payload: dict) -> "MTGIOCard":
        """
        Create an MTGIOCard instance from a payload dictionary.
        The payload is expected to have keys matching the MTGIOCard fields.
        """
        return cls(
            names=[payload.get("name", "")],
            mana_cost=payload.get("manaCost", ""),
            colors=payload.get("colors", []),
            color_identity=payload.get("colorIdentity", []),
            types=payload.get("types", []),
            power=payload.get("power", ""),
            toughness=payload.get("toughness", ""),
            rarity=CardRarity.__members__.get(payload.get("rarity", "common").upper()) or CardRarity.COMMON,
            subtypes=payload.get("subtypes", []),
            supertypes=payload.get("supertypes", []),
            text=payload.get("text"),
            flavor=payload.get("flavor", ""),
            layout=payload.get("layout", "normal"),
            rulings=[MTGCardRuling(**ruling) for ruling in payload.get("rulings", [])],
            foreign_names=[MTGCardAlias(**name) for name in payload.get("foreignNames", [])],
            printings=payload.get("printings", []),
            id=payload["id"],
            image_url=payload.get("imageUrl", ""),
        )

    @field_validator("printings", mode="after")
    @classmethod
    def validate_printings(cls, printings: list[str]) -> list[str]:
        """Ensure printings are unique and sorted."""
        if not printings:
            raise ValueError("Printings cannot be empty.")

        if not all(isinstance(p, str) for p in printings):
            raise ValueError("All printings must be strings.")

        if any(len(p) == 0 for p in printings):
            raise ValueError("Printings cannot contain empty strings.")

        unique_printings = sorted(set(map(lambda string: string.upper(), printings)))
        return unique_printings

    @field_validator("mana_cost", mode="after")
    @classmethod
    def check_mana_cost_format(cls, value: str) -> str:
        """Validate the mana cost format."""
        if not re.match(cls.MANA_COST_REGEX, value):
            raise ValueError(cls.INVALID_MANA_COST_ERROR.format(value=value))
        return value

    @field_validator("names", mode="after")
    @classmethod
    def validate_names(cls, names: list[str]) -> list[str]:
        """Ensure names are unique and sorted."""
        if not names:
            raise ValueError("Names cannot be empty.")

        if not all(isinstance(name, str) for name in names):
            raise ValueError("All names must be strings.")

        if any(len(name) == 0 for name in names):
            raise ValueError("Names cannot contain empty strings.")

        unique_names = sorted(set(map(lambda string: string.strip(), names)))
        return unique_names

    @property
    def keywords(self) -> list[Keyword]:
        return self.extract_keywords_from_card_text(self.text)

    @classmethod
    def extract_keywords_from_card_text(cls, text: str | None) -> list[Keyword]:
        """Extract keywords from the card text."""
        if not text:
            return []
        keywords = []
        for keyword in Keyword:
            if keyword.value.lower() in text.lower():
                keywords.append(keyword)
        return keywords

    def __eq__(self, other: object) -> bool:
        """Check equality based on the card's unique identifier."""
        if not isinstance(other, MTGIOCard):
            return NotImplemented

        names_match = self.names == other.names
        mana_cost_match = self.mana_cost == other.mana_cost
        colors_match = self.colors == other.colors
        return names_match and mana_cost_match and colors_match


class MTGCard(BaseModel):
    """Represents a Magic: The Gathering card."""

    id: str = Field(..., description="Unique identifier for the card")
    name: str = Field(..., description="Name of the card")
    aliases: list[MTGCardAlias] = Field(default_factory=list, description="List of foreign names for the card")
    rulings: list[MTGCardRuling] = Field(default_factory=list, description="List of rulings for the card")
    mana_value: ManaValue = Field(..., description="Mana value of the card")
    types: list[str] = Field(default_factory=list, description="List of types the card belongs to")
    subtypes: list[str] = Field(default_factory=list, description="List of subtypes the card belongs to")
    keywords: list[Keyword] = Field(default_factory=list, description="List of counters on the card")
    text: str | None = Field(default="", description="Text on the card, such as rules text or abilities")
    flavor: str = Field(default="", description="Flavor text of the card, if any")
    power: str | None = Field(None, description="Power of the creature card")
    toughness: str | None = Field(None, description="Toughness of the creature card")
    rarity: str | None = Field(None, description="Rarity of the card")
    set_name: str | None = Field(None, description="Set name where the card belongs")
    image_url: str | None = Field(default="", description="URL to the card's image")

    def __str__(self) -> str:
        """Return a string representation of the card."""
        return f"{self.name} ({self.id}) - {self.set_name or 'Unknown Set'}"

    @classmethod
    def from_mtgio_card(cls, card: MTGIOCard) -> "MTGCard":
        """Convert MTGIOCard to MTGCard."""
        logging.info(f"Converting MTGIOCard '{card.names[0]}' with ID '{card.id}' to MTGCard.")
        return cls(
            id=card.id,
            name=card.names[0],
            aliases=card.foreign_names,
            rulings=card.rulings,
            mana_value=ManaValue.from_mtgio_cost_string(card.mana_cost),
            types=card.types,
            subtypes=card.subtypes,
            keywords=card.keywords,
            text=card.text,
            flavor=card.flavor,
            power=card.power,
            toughness=card.toughness,
            rarity=card.rarity,
            set_name=card.printings[0] if card.printings else None,
            image_url=card.image_url,
        )

    @classmethod
    def null(cls) -> Any:
        return None
