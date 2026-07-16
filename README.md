# Code and data for Who Owns the AI Economy?

Code and data behind the two computed figures in
[**"Who Owns the AI Economy?"**](https://silviupitis.com/blog/2026/who-owns-the-ai-economy/).

| Directory | Essay figure | What it computes |
|---|---|---|
| [`figure3-club/`](figure3-club/) | **Figure 3**, the enforcement-club ledger | What each country collects as it joins a club that levies large firms according to where they sell, and what a holdout leaves on the table |
| [`figure4-fund/`](figure4-fund/) | **Figure 4**, the fund-dividend paths | A fifty-year public dividend per person under three AI scenarios, as a public fund gradually accumulates covered equity |

## Quickstart

Python 3.10 or later is required. Node.js is optional and is used only for the
browser-model tests.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# Figure 3
cd figure3-club
python3 figure3.py
python3 figure3.py --render

# Figure 4
cd ../figure4-fund
python3 -m unittest
python3 figure4.py
python3 figure4.py --render
node web/test_models.js
```

Rendering the PNG assets requires the Cairo system library. The numerical
reports and tests do not.

## AI Disclosure

The code, documentation, and data in this repo were written and sourced largely
by GPT and Claude, working from my specifications. I reviewed the modeling
logic and assumptions and spot checked the data. The Fig 4 model is
cross-checked using an alternative model. How AI contributed to the essay
itself is described in the
[acknowledgements](https://silviupitis.com/blog/2026/who-owns-the-ai-economy/#acknowledgements).

## License

MIT. See [LICENSE](LICENSE).
