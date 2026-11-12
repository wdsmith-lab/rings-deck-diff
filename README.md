# rings-deck-diff

Lord of the Rings LCG deck diff tool for comparing two RingsDB decks and showing which cards to remove and which to add in order to turn deck 1 into deck 2.

## What it does

This tool helps you migrate from one published RingsDB deck to another by showing a clear list of:

- cards to remove from the first deck
- cards to add to turn it into the second deck

It is especially useful when comparing similar decks or tracking the changes between a deck and a later variant.

## Example usage

```bash
python3 rings-diff-cli.py 8682 15839
```

This compares the first deck ID to the second and prints the card-by-card delta between them.

## Reference deck pair

These are a good pair to try because they are well known and one is derived from the other:

- `8682`
- `15839`

You can compare them directly with:

```bash
python3 rings-diff-cli.py 8682 15839
```

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

- Decks must be published (public) on RingsDB. Support for private decks is planned.
