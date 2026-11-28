# How atlas.json is built

Run in this order (Python 3, no extra packages):

1. `build_all.py`: reads `itin.py` (hand-written itineraries and notes for all 12 journeys) and `bible/fact/journeys.json` (Theographic routes). It fits a route line to each leg, measures miles, and marks sea legs by testing against the coastlines in `map.json`.
2. `match_all.py`: matches each place to OpenBible.info Bible Geocoding (`data/ancient.jsonl`, `data/modern.jsonl` from github.com/openbibleinfo/Bible-Geocoding-Data) and to Pleiades (through Wikidata, using github.com/isawnyu/pleiades_wikidata, then the per-place JSON in isawnyu/pleiades.datasets).
3. `assemble.py`: writes `bible/fact/atlas.json`.

The paths at the top of the scripts point to the build machine. Change them to where you cloned the two data repos.

Terrain images (`relief_*.jpg`) are crops of Tom Patterson's shaded relief (public domain), tinted to match the old-map style.
