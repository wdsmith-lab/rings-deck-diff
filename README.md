# rings-deck-diff (Lord of the Rings LCG deck diff tool)
Easily migrate from one ringsdb.com deck to another (indicating which cards to remove, and which cards to add to turn deck1 into deck2)

> [!NOTE] Usage
> **python3 rings-diff-cli.py [-h] [-c] deck1_id deck2_id**
> 
> positional arguments:
>  deck1_id        ID of the first deck
>  deck2_id        ID of the second deck
>
> options:
>  -h, --help      show help message and exit
>  -c, --no-color  Disable colorized output


**Current limitations:**

    - Decks must be published (public) on Ringsdb.com.  Support for private decks is planned.
