# rings-deck-diff

A small utility for comparing two published RingsDB decks and showing exactly what to remove and add to transform one into the other.

## Overview

If you are moving from one Lord of the Rings LCG deck to another, this tool helps you see the delta at a glance:

- cards to remove from the first deck
- cards to add to reach the second deck
- a quick way to compare deck variants and deck updates

This is especially useful when you want to migrate a deck without manually checking each card.

## Example

```bash
python3 rings-diff-cli.py 8682 15839
```

This compares the first deck ID to the second and prints the card-by-card changes between them.

## Good reference decks

These are a strong pair to try because they are well known and one is derived from the other:

- `8682`
- `15839`

## Usage

```bash
python3 rings-diff-cli.py [-h] [-c] deck1_id deck2_id
```

### Positional arguments

- `deck1_id`: ID of the first deck
- `deck2_id`: ID of the second deck

### Options

- `-h`, `--help`: Show the help message and exit
- `-c`, `--no-color`: Disable colorized output

## Current limitations

- Decks must be published (public) on RingsDB.
- Support for private decks is planned.
