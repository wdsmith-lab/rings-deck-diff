import sys
import requests
import json
from collections import Counter
from typing import Dict
from dataclasses import dataclass

@dataclass
class CardData:
    code: int
    name: str
    sphere_name: str
    type: str
    pack_code: str

@dataclass
class DeckData:
    deck_id: int
    name: str
    slots: Counter

@dataclass
class MigrationOutput:
    deck1: DeckData
    deck2: DeckData
    cards_to_remove_slots: Counter
    cards_to_add_slots: Counter
    card_map_to_remove: Dict[str, CardData]
    card_map_to_add: Dict[str, CardData]
    card_name_width: int

    def __str__(self) -> str:
        output = (
            f"\n{Color.CLR_CYN}=== MIGRATION PATH FROM {self.deck1.deck_id} "
            f"(\"{self.deck1.name}\") to {self.deck2.deck_id} "
            f"(\"{self.deck2.name}\") ==={Color.CLR_RST}"
        )
        output += self._format_card_changes(
            "[-] CARDS TO REMOVE FROM DECK 1",
            "Remove",
            Color.CLR_RED,
            self.cards_to_remove_slots,
            self.card_map_to_remove,
        )
        output += self._format_card_changes(
            "[+] CARDS TO ADD TO DECK 1",
            "Add",
            Color.CLR_GRN,
            self.cards_to_add_slots,
            self.card_map_to_add,
        )
        return output

    def _get_sphere_color(self, sphere_name: str) -> str:
        match sphere_name:
            case "Fellowship":
                return Color.CLR_YLW
            case "Leadership":
                return Color.CLR_MAG
            case "Lore":
                return Color.CLR_GRN
            case "Spirit":
                return Color.CLR_BLU
            case "Tactics":
                return Color.CLR_RED
            case "Neutral":
                return Color.CLR_WHT        
            case _:
                return Color.CLR_RST

    def _format_card_changes(
        self,
        heading: str,
        action: str,
        action_color: str,
        slots: Counter,
        cards: Dict[str, CardData],
    ) -> str:
        output = f"\n\n{heading}:"
        if not slots:
            output += "   None!"

        for card_id, card_data in cards.items():
            output += (
                f"\n  {action_color}{action} {slots[card_id]}x "
                + pad_string_to_length(card_data.name, self.card_name_width)
                + pad_string_to_length(f"(#{card_id}){Color.CLR_RST}", 13)
                + " "
                + pad_string_to_length(
                    f"[{self._get_sphere_color(card_data.sphere_name)}{card_data.sphere_name}{Color.CLR_RST}]",
                    23,
                )
                + pad_string_to_length(f" [{card_data.type}]", 15)
                + pad_string_to_length(f" (from pack: {card_data.pack_code})", 20)
            )
        return output

@dataclass
class Color:
    # ANSI Color Codes
    CLR_BLU: str = "\033[34m"
    CLR_RED: str = "\033[31m"
    CLR_GRN: str = "\033[32m"
    CLR_MAG: str = "\033[35m"
    CLR_CYN: str = "\033[36m"
    CLR_YLW: str = "\033[33m"
    CLR_WHT: str = "\033[37m"
    CLR_RST: str = "\033[0m"

def get_deck_data(deck_id):
    url: str = f"https://ringsdb.com/api/public/decklist/{deck_id}.json"
    http_response: requests.Response = requests.get(url)

    raw_deck_data: dict = http_response.json()
    deck_data: DeckData = DeckData(deck_id, raw_deck_data.get("name", "Unknown Deck"), Counter(raw_deck_data.get("slots", {})))
    return deck_data

def get_card_map() -> Dict[str, CardData]:
    all_cards: list

    try:
        with open('cardlist.json', 'r', encoding='utf-8') as file:
            print("Local cardlist.json found, loading...")
            all_cards = json.load(file)
    
    except FileNotFoundError:
        print("cardlist.json not found, creating...")
        # Don't want to spam the server with individual card reqests, so fetch entire global card catalog at once
        url: str = "https://ringsdb.com/api/public/cards/"
        response: requests.Response = requests.get(url)
        all_cards = response.json()

        with open("cardlist.json", "w", encoding="utf-8") as file:
            json.dump(all_cards, file, indent=4)
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in cardlist.json. Broken at line {e.lineno}, column {e.colno}.")

    # DEBUG: temp for analyzing structure of all_cards
    #tempcard = all_cards[1]
    #print(tempcard)
    #sys.exit()
    # END DEBUG BLOCK

    dict: Dict = {}
    for card in all_cards:

        card_data = CardData(card["code"], card["name"], card["sphere_name"], card["type_name"], card["pack_code"])
        dict[card["code"]] = card_data
   
    return dict


def pad_string_to_length(input_str, length) -> str:
    return input_str.ljust(length)

def strip_ansi_escape_codes(input_str) -> str:
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', input_str)

def main():
    # Check if arguments were passed
    if len(sys.argv) > 2:
        script_name: str = sys.argv[0]
        # TODO: Try/Catch and fail gracefully with an error message if ValueError
        deck1_id: int = int(sys.argv[1])
        deck2_id: int = int(sys.argv[2])

        print(f"Running script: {script_name}")
        print(f"Deck 1 ID: {deck1_id}")
        print(f"Deck 2 ID: {deck2_id}")
    else:
        print("Two command line arguments (RingsDB deck id numbers) must be provided.")
        sys.exit()

    colorize: bool = True # TODO: Add command line argument to disable colorization for Windows cmd.exe users

    deck1: DeckData = get_deck_data(deck1_id)
    deck2: DeckData = get_deck_data(deck2_id)
    # TODO: exit with error message if one of the decks can not be loaded (empty Counter)

    card_map_full: Dict[str, CardData] = get_card_map()

    #print(card_map)
    #sys.exit()

    # Returns 0 if the dictionary is completely empty
    card_name_longest_length: int = max((len(card.name) for card in card_map_full.values()), default=0)

    cards_to_add_slots: Counter = deck2.slots - deck1.slots
    cards_to_remove_slots: Counter = deck1.slots - deck2.slots
    card_map_to_add: Dict[str, CardData] = {k: v for k, v in card_map_full.items() if k in cards_to_add_slots}
    card_map_to_remove: Dict[str, CardData] = {k: v for k, v in card_map_full.items() if k in cards_to_remove_slots}

    #print(list(card_map_to_add.values()))
    #sys.exit()

    # TODO: Allow for multiple sorting methods, e.g. by name, by sphere, by type, etc.
    # For now, sort by sphere, then by type, then by name
    card_map_to_add = dict(sorted(card_map_to_add.items(), key=lambda item: (item[1].sphere_name, item[1].type, item[1].name)))
    card_map_to_remove = dict(sorted(card_map_to_remove.items(), key=lambda item: (item[1].sphere_name, item[1].type, item[1].name)))

    migration_output = MigrationOutput(
        deck1,
        deck2,
        cards_to_remove_slots,
        cards_to_add_slots,
        card_map_to_remove,
        card_map_to_add,
        card_name_longest_length,
    )

    if colorize:
        print(migration_output)
    else:
        print(strip_ansi_escape_codes(str(migration_output)))

if __name__ == "__main__":
    main()


