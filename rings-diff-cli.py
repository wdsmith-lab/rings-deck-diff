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
    sphere_color: str

@dataclass
class DeckData:
    deck_id: int
    name: str
    slots: Counter

@dataclass
class Color:
    # ANSI Color Codes
    CLR_BLU: str = "\033[34m"
    CLR_RED: str  = "\033[31m"
    CLR_GRN: str = "\033[32m"
    CLR_MAG: str = "\033[35m"
    CLR_CYN: str = "\033[36m"
    CLR_YLW: str = "\033[33m"
    CLR_RST: str = "\033[0m"

def get_deck_data(deck_id):
    # I like declaring types, coming from strongly typed language backgrounds
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
        sphere_color: str

        match card["sphere_name"]:
            case "Fellowship":
                sphere_color = Color.CLR_YLW
            case "Leadership":
                sphere_color = Color.CLR_MAG
            case "Lore":
                sphere_color = Color.CLR_GRN
            case "Spirit":
                sphere_color = Color.CLR_BLU
            case "Tactics":
                sphere_color = Color.CLR_RED        
            case _:
                sphere_color = Color.CLR_RST

        card_data = CardData(card["code"], card["name"], card["sphere_name"], sphere_color)
        dict[card["code"]] = card_data
   
    return dict


def pad_string_to_length(input_str, length) -> str:
    return input_str.ljust(length)

### Begin main

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

deck1: DeckData = get_deck_data(deck1_id)
deck2: DeckData = get_deck_data(deck2_id)
# TODO: exit with error message if one of the decks can not be loaded (empty Counter)

card_map: Dict = get_card_map()

# Returns 0 if the dictionary is completely empty
card_name_longest_length: int = max((len(card.name) for card in card_map.values()), default=0)

cards_to_add: Counter = deck2.slots - deck1.slots
cards_to_remove: Counter = deck1.slots - deck2.slots

name: str

print(f"\n{Color.CLR_CYN}=== MIGRATION PATH FROM {deck1_id} \"({deck1.name}\") to {deck2_id} (\"{deck2.name}\") ==={Color.CLR_RST}")

print("\n[-] CARDS TO REMOVE FROM DECK 1:")
if not cards_to_remove:
    print("   None!")
for card_id, qty in cards_to_remove.items():
    card_data: CardData = card_map.get(card_id, card_id)
    print(f"  {Color.CLR_RED}Remove {qty}x " + pad_string_to_length(card_data.name, card_name_longest_length) + f" (#{card_id}){Color.CLR_RST}" + f" [{card_data.sphere_color}{card_data.sphere_name}{Color.CLR_RST}]")    

print("\n[+] CARDS TO ADD TO DECK 1:")
if not cards_to_add:
    print("   None!")
for card_id, qty in cards_to_add.items():
    card_data = card_map.get(card_id, card_id)
    print(f"  {Color.CLR_GRN}Add {qty}x " + pad_string_to_length(card_data.name, card_name_longest_length) + f" (#{card_id}){Color.CLR_RST}" + f" [{card_data.sphere_color}{card_data.sphere_name}{Color.CLR_RST}]")






