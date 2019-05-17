# 80 Points

A trick-based game where teams of players earn points to advance their levels.

Rules: https://en.wikipedia.org/wiki/Sheng_ji

## Setup 

```bash
# Creates a directory to hold dependencies
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies needed
pip install -r requirements.txt
```

## Run the server

```bash
python3 server/server.py
```

## Run unit tests

```bash
# Run a single test (run under server/)
python3 -m unittest model_test.py

# Runs all tests (run under server/)
python3 -m unittest *_test.py

# Run using `pytest`, can be run from anywhere (make sure `pytest` is installed)
pytest
```

## Testing with a deterministic deck

To use a deterministic test deck, add a file under `server/testdata/` ending
in .txt, e.g. `declaration.txt`.

### Format of test data file

The first four lines correspond to player hands, and the cards are dealt
in order that they appear on the line. The last line corresponds to the
bottom (order is not preserved for the bottom). Each card is represented as
`<suit_initial><value>`, where `<suit_initial>` is the first letter in the
suit, e.g. 'h' for 'hearts' and 'j' for 'joker', and `value` is the value
as found in `CARD_VALUES`, e.g. '2' or 'J'.

For example, if the file looked like:

```
d2 d3 d4 ...
h2 h3 h4 ...
s2 s3 s4 ...
c2 c3 c4 ...
jbig jbig jsmall jsmall dA hA sA cA
```

Then the first card dealt will be a 2 of diamonds to hand 0. The second card
dealt will be 2 of heards to hand 1, then 2 of spades to hand 2, 2 of clubs
to hand 3, 3 of diamonds to hand 0, and so on.

### Usage with server

To use the deterministic deck, run:

```bash
python3 server/server.py --deck_name=<deck_name>
```

where `<deck_name>` is the name of the file without the .txt extension in the
testdata directory. For example, if the file path was 
`server/testdata/declaration.txt`, you would pass `--deck_name=declaration`.