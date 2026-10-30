import sys
import requests
import json
from collections import Counter
from typing import Dict

def get_deck_slots(deck_id):
    # I like declaring types, coming from strongly typed language backgrounds
    url: str = f"https://ringsdb.com/api/public/decklist/{deck_id}.json"
    http_response: requests.Response = requests.get(url)
    #return Counter(response.get("slots", {}))
    deck_data: dict = http_response.json()
    return Counter(deck_data.get("slots", {}))

def get_card_map() -> Dict[str, str]:
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

    # map card code to card name, ie: {"01001": "Aragorn", "01003": "Steward of Gondor"}
    return {card["code"]: card["name"] for card in all_cards}

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

deck1: Counter = get_deck_slots(deck1_id)
deck2: Counter = get_deck_slots(deck2_id)
# TODO: exit with error message if one of the decks can not be loaded (empty Counter)

card_map: Dict = get_card_map()
card_name_longest_length: int = len(max(card_map.values(), key=len))

# Pull unique cards IDs present across both deck
# TODO: Is this actually used, ultimately?
#all_card_ids = set(deck1.keys()) | set(deck2.keys())

cards_to_add: Counter = deck2 - deck1
cards_to_remove: Counter = deck1 - deck2

# ANSI Color Codes
CLR_RED: str  = "\033[31m"
CLR_GRN: str = "\033[32m"
CLR_CYN: str = "\033[36m"
CLR_RST: str = "\033[0m"

name: str

print(f"\n{CLR_CYN}=== MIGRATION PATH FROM {deck1_id} to {deck2_id} ==={CLR_RST}")

print("\n[-] CARDS TO REMOVE FROM DECK 1:")
if not cards_to_remove:
    print("   None!")
for card_id, qty in cards_to_remove.items():
    name = card_map.get(card_id, card_id)
    print(f"  {CLR_RED}Remove {qty}x " + pad_string_to_length(name, card_name_longest_length) + f" (#{card_id}){CLR_RST}")    

print("\n[+] CARDS TO ADD TO DECK 1:")
if not cards_to_add:
    print("   None!")
for card_id, qty in cards_to_add.items():
    name = card_map.get(card_id, card_id)
    print(f"  {CLR_GRN}Add {qty}x " + pad_string_to_length(name, card_name_longest_length) + f" (#{card_id}){CLR_RST}")  






