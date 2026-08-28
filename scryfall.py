import gzip
import json
import logging
import re
import datetime
from pathlib import Path

import requests

from scryfall_cfg import OVERRIDES
from card import Card

BULK_DATA_LIST_URL = 'https://api.scryfall.com/bulk-data'
REQUEST_HEADERS = {
    'User-Agent': 'JoelCubeTools/1.0 (personal cube management; oelarnes@gmail.com)',
    'Accept': 'application/json',
}

CACHE_DIR = Path(__file__).parent / 'cache'
CARDS_FILE = CACHE_DIR / 'scryfall_cards.json'
META_FILE = CACHE_DIR / 'scryfall_meta.json'

DRAFTABLE_SET_TYPES = {'draft_innovation', 'expansion', 'commander', 'planechase', 'core', 'starter', 'funny'}
EXCLUDED_FRAME_EFFECTS = {'showcase', 'extendedart', 'borderless'}
EXCLUDED_PROMO_TYPES = {'serialized'}


def refresh_cache():
    bulk_data_result = requests.get(BULK_DATA_LIST_URL, headers=REQUEST_HEADERS)
    bulk_data_result.raise_for_status()
    entries = bulk_data_result.json()['data']
    default_cards_entry = next(e for e in entries if e['type'] == 'default_cards')
    download_uri = default_cards_entry['jsonl_download_uri']

    download = requests.get(download_uri, headers=REQUEST_HEADERS)
    download.raise_for_status()
    raw = gzip.decompress(download.content)
    cards = [json.loads(line) for line in raw.splitlines() if line]

    print('{} pulled'.format(len(cards)))

    CACHE_DIR.mkdir(exist_ok=True)
    with open(CARDS_FILE, 'w') as f:
        json.dump(cards, f)

    with open(META_FILE, 'w') as f:
        json.dump({
            'as_of': f'{datetime.datetime.now(datetime.UTC).isoformat(timespec="milliseconds")}Z',
            'count': len(cards),
        }, f)

    print(f'{len(cards)} cards written to {CARDS_FILE}')


def _card_is_preferred_variant(card):
    if set(card.get('frame_effects') or []) & EXCLUDED_FRAME_EFFECTS:
        return False
    if set(card.get('promo_types') or []) & EXCLUDED_PROMO_TYPES:
        return False
    return True


def _collector_number_sort_key(card):
    # collector numbers are strings and sometimes carry non-numeric suffixes
    # ("12a", "142s" for a foreign alt art, "17★" for a foil-only variant) that
    # mark a bonus/alternate printing of the same base number; prefer the bare
    # number ("49" < "149", and "17" < "17★") over any suffixed variant
    collector_number = card.get('collector_number') or ''
    match = re.match(r'^(\d+)(.*)$', collector_number)
    if not match:
        return (1, 0, 0, collector_number)
    number, suffix = match.groups()
    return (0, int(number), 0 if suffix == '' else 1, suffix)


class Scryfall:
    def __init__(self, sets=None):
        self._sets = sets  # only query for these sets
        self._by_name = {}
        self._by_face_name = {}
        # printed_name / flavor_name (reskins like om1, Secret Lair flavor names) -> the card's real name,
        # so a lookup by alt name still resolves to the preferred (earliest booster) printing of that card
        self._alt_to_canonical = {}
        self._by_mtgo_id = {}
        self._load()

    def _load(self):
        if not CARDS_FILE.exists():
            raise FileNotFoundError(
                f'No local Scryfall cache at {CARDS_FILE}. Run scryfall_cache.py first.'
            )

        with open(CARDS_FILE) as f:
            cards = json.load(f)

        for card in cards:
            self._by_name.setdefault(card['name'], []).append(card)

            for alt_key in ('printed_name', 'flavor_name'):
                alt = card.get(alt_key)
                if alt:
                    self._alt_to_canonical.setdefault(alt, card['name'])

            for face in card.get('card_faces', []):
                if 'name' in face:
                    self._by_face_name.setdefault(face['name'], []).append(card)
                for alt_key in ('printed_name', 'flavor_name'):
                    alt = face.get(alt_key)
                    if alt:
                        self._alt_to_canonical.setdefault(alt, face['name'])

            for id_key in ('mtgo_id', 'mtgo_foil_id'):
                if card.get(id_key) is not None:
                    self._by_mtgo_id[card[id_key]] = card

    def _candidates_for_set(self, candidates, set, restrict_to_draftable):
        if set is not None:
            return [c for c in candidates if c.get('set') == set]
        if self._sets is not None:
            return [c for c in candidates if c.get('set') in self._sets]
        if restrict_to_draftable:
            return [c for c in candidates if c.get('set_type') in DRAFTABLE_SET_TYPES]
        return candidates

    def get_card(self, card_name, set=None):
        card_name = OVERRIDES['names'].get(card_name, card_name)
        card_name = self._alt_to_canonical.get(card_name, card_name)

        candidates = self._by_name.get(card_name, []) + self._by_face_name.get(card_name, [])
        matches = self._candidates_for_set(
            [c for c in candidates if _card_is_preferred_variant(c)], set, restrict_to_draftable=True
        )

        if not matches:
            # broaden: any printing/frame, excluding memorabilia (tokens, art cards, etc.)
            candidates = [c for c in candidates if c.get('set_type') != 'memorabilia']
            matches = self._candidates_for_set(candidates, set, restrict_to_draftable=False)

        if not matches:
            error_message = 'No match for card name {}'.format(card_name)
            if set is not None:
                error_message = error_message + ' and set {}'.format(set)
            logging.warning(error_message)
            return Card({'name': card_name})

        matches.sort(key=lambda c: (
            0 if 'paper' in (c.get('games') or []) else 1,
            0 if c.get('lang') == 'en' else 1,
            c.get('released_at') or '',
            _collector_number_sort_key(c),
        ))
        return Card(matches[0])

    def get_card_by_id(self, mtgo_id):
        card = self._by_mtgo_id.get(int(mtgo_id))

        if card is None:
            logging.error('No match for card id {}'.format(mtgo_id))

        return Card(card)
