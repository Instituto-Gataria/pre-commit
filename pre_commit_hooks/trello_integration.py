#!/usr/bin/env python3

import os
import re
import sys
import requests
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(asctime)s] [Trello Integration] %(message)s', datefmt='%d/%b/%Y:%H:%M:%S')

TOKEN = os.getenv('TRELLO_TOKEN')
API_KEY = os.getenv('TRELLO_API_KEY')
BOARD_ID = os.getenv('TRELLO_BOARD_ID')
LIST_IDS = os.getenv('TRELLO_LIST_IDS').split(',')

COMMIT_TYPES = ['feature', 'hotfix', 'chore', 'bugfix', 'docs', 'style', 'refactor', 'test', 'revert']

def get_cards():
    logging.info(f"Retrieving cards from board_id ${BOARD_ID} and list_ids ${LIST_IDS}")

    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards?key={API_KEY}&token={TOKEN}"
    response = requests.get(url)

    cards = response.json()
    filtered_cards = [card for card in cards if card['idList'] in LIST_IDS]

    return filtered_cards

def validate_commit_message(message, cards):
    # Check for pattern: [firstEightDigitsOfValidCard-commitType]
    match = re.search(r'\[(\w{8})-(\w+)\]', message)

    if not match:
        return False

    card_id_part, commit_type = match.groups()

    # Check if card_id_part is the beginning of any valid card ID
    valid_card = any(card['id'].startswith(card_id_part) for card in cards)

    # Check if commit_type is valid
    valid_type = commit_type in COMMIT_TYPES

    return valid_card and valid_type

def main():
    cards = get_cards()

    if not cards:
        logging.info("No cards found.")
        sys.exit(1)

    # Fetch the commit message. This assumes that the message is passed as the first argument.
    with open(sys.argv[1], 'r') as f:
        commit_message = f.read().strip()

    if not validate_commit_message(commit_message, cards):
        card_info = [f"{card['id'][:8]} ({card['name']})" for card in cards]
        logging.info("Invalid commit message format or referenced card.")
        logging.info("Commit message should follow the format: [firstEightDigitsOfValidCard-commitType]")
        logging.info("Valid commit types are: %s", ", ".join(COMMIT_TYPES))
        logging.info("Valid card IDs and names are: %s", ", ".join(card_info))
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
