#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update data/watched.yaml with TMDB IDs and localized posters.

Usage:
  python scripts/update_tmdb.py --token <TMDB_READ_ACCESS_TOKEN>

Notes:
- Prefers IMDb ID matching; falls back to Douban ID lookup.
- Adds tmdb_id, title_en, poster (zh default), poster_en (en default).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Optional

import requests
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"
DOUBAN_API_BASE = "https://douban-api.edui.fun/v2/movie/subject/"


def http_get_json(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    resp = requests.get(url, headers=headers, params=params, timeout=25)
    resp.raise_for_status()
    return resp.json()


def tmdb_get(path: str, token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }
    return http_get_json(f"{TMDB_API_BASE}{path}", headers=headers, params=params)


def try_tmdb_get(
    path: str,
    token: str,
    params: Optional[Dict[str, Any]] = None,
    allow_404: bool = False,
) -> Optional[Dict[str, Any]]:
    try:
        return tmdb_get(path, token, params=params)
    except requests.HTTPError as exc:
        if allow_404 and exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def normalize_imdb_id(item: Dict[str, Any]) -> Optional[str]:
    imdb_val = item.get("imdb_id")
    imdb_id = str(imdb_val).strip() if imdb_val is not None else ""
    if imdb_id and imdb_id.startswith("tt"):
        return imdb_id

    item_id_val = item.get("id")
    item_id = str(item_id_val).strip() if item_id_val is not None else ""
    if item_id.startswith("tt"):
        # Use item id when it looks like imdb id
        return item_id

    if imdb_id and imdb_id.isdigit():
        return f"tt{imdb_id}"

    return None


def content_type_to_tmdb(item: Dict[str, Any]) -> str:
    ctype = (item.get("content_type") or "").lower()
    if ctype in {"tvshow", "tv_series", "tv", "series", "variety"}:
        return "tv"
    return "movie"


def tmdb_find_by_imdb(imdb_id: str, token: str, prefer: str) -> Optional[Dict[str, Any]]:
    data = tmdb_get(f"/find/{imdb_id}", token, params={"external_source": "imdb_id"})
    movie_results = data.get("movie_results") or []
    tv_results = data.get("tv_results") or []
    if prefer == "tv":
        return (tv_results[0] if tv_results else None) or (movie_results[0] if movie_results else None)
    return (movie_results[0] if movie_results else None) or (tv_results[0] if tv_results else None)


def douban_lookup(douban_id: str) -> Optional[Dict[str, Any]]:
    try:
        data = http_get_json(f"{DOUBAN_API_BASE}{douban_id}")
        return data
    except Exception:
        return None


def tmdb_search_by_title(
    title: str,
    token: str,
    prefer: str,
    year: Optional[str] = None,
    language: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if not title:
        return None

    params: Dict[str, Any] = {
        "query": title,
        "include_adult": "false",
    }
    if language:
        params["language"] = language
    if year:
        if prefer == "tv":
            params["first_air_date_year"] = year
        else:
            params["year"] = year

    endpoint = "/search/tv" if prefer == "tv" else "/search/movie"
    data = tmdb_get(endpoint, token, params=params)
    results = data.get("results") or []
    return results[0] if results else None


def pick_best_poster(posters: List[Dict[str, Any]], langs: List[Optional[str]]) -> Optional[str]:
    for lang in langs:
        if lang is None:
            candidates = [p for p in posters if p.get("iso_639_1") is None]
        else:
            candidates = [p for p in posters if p.get("iso_639_1") in {lang}]
        if candidates:
            candidates.sort(key=lambda p: (p.get("vote_count") or 0, p.get("vote_average") or 0), reverse=True)
            return candidates[0].get("file_path")
    return None


def tmdb_posters(tmdb_id: int, token: str, media_type: str) -> Dict[str, Optional[str]]:
    data = try_tmdb_get(
        f"/{media_type}/{tmdb_id}/images",
        token,
        params={"include_image_language": "zh,en,null"},
        allow_404=True,
    )
    if data is None:
        alt_type = "tv" if media_type == "movie" else "movie"
        data = try_tmdb_get(
            f"/{alt_type}/{tmdb_id}/images",
            token,
            params={"include_image_language": "zh,en,null"},
            allow_404=True,
        )

    posters = (data or {}).get("posters") or []

    zh_path = pick_best_poster(posters, ["zh", "zh-CN", None])
    en_path = pick_best_poster(posters, ["en", None])

    return {
        "zh": f"{TMDB_IMAGE_BASE}{zh_path}" if zh_path else None,
        "en": f"{TMDB_IMAGE_BASE}{en_path}" if en_path else None,
    }


def tmdb_title_en(tmdb_id: int, token: str, media_type: str) -> Optional[str]:
    data = try_tmdb_get(f"/{media_type}/{tmdb_id}", token, params={"language": "en-US"}, allow_404=True)
    if data is None:
        alt_type = "tv" if media_type == "movie" else "movie"
        data = try_tmdb_get(f"/{alt_type}/{tmdb_id}", token, params={"language": "en-US"}, allow_404=True)
    if not data:
        return None
    return data.get("title") or data.get("name") or data.get("original_title") or data.get("original_name")


def tmdb_title_en(tmdb_id: int, token: str, media_type: str) -> Optional[str]:
    data = tmdb_get(f"/{media_type}/{tmdb_id}", token, params={"language": "en-US"})
    return data.get("title") or data.get("name") or data.get("original_title") or data.get("original_name")


def move_key_after(item: CommentedMap, key: str, after_key: str) -> None:
    if key not in item or after_key not in item:
        return
    keys = list(item.keys())
    if key not in keys or after_key not in keys:
        return
    if keys.index(key) == keys.index(after_key) + 1:
        return
    value = item.pop(key)
    new_map = CommentedMap()
    for k in keys:
        if k == key:
            continue
        new_map[k] = item[k]
        if k == after_key:
            new_map[key] = value
    item.clear()
    item.update(new_map)


def move_key_before(item: CommentedMap, key: str, before_key: str) -> None:
    if key not in item or before_key not in item:
        return
    keys = list(item.keys())
    if key not in keys or before_key not in keys:
        return
    if keys.index(key) == keys.index(before_key) - 1:
        return
    value = item.pop(key)
    new_map = CommentedMap()
    for k in keys:
        if k == key:
            continue
        if k == before_key:
            new_map[key] = value
        new_map[k] = item[k]
    item.clear()
    item.update(new_map)


def ensure_tmdb_position(item: CommentedMap) -> None:
    if "tmdb_id" not in item:
        return
    if "imdb_id" in item:
        move_key_after(item, "tmdb_id", "imdb_id")
    elif "douban_id" in item:
        move_key_before(item, "tmdb_id", "douban_id")


def ensure_title_en_position(item: CommentedMap) -> None:
    if "title_en" not in item:
        return
    if "title" in item:
        move_key_after(item, "title_en", "title")


def move_key_before(item: CommentedMap, key: str, before_key: str) -> None:
    if key not in item or before_key not in item:
        return
    keys = list(item.keys())
    if key not in keys or before_key not in keys:
        return
    if keys.index(key) == keys.index(before_key) - 1:
        return
    value = item.pop(key)
    new_map = CommentedMap()
    for k in keys:
        if k == key:
            continue
        if k == before_key:
            new_map[key] = value
        new_map[k] = item[k]
    item.clear()
    item.update(new_map)


def ensure_tmdb_position(item: CommentedMap) -> None:
    if "tmdb_id" not in item:
        return
    if "imdb_id" in item:
        move_key_after(item, "tmdb_id", "imdb_id")
    elif "douban_id" in item:
        move_key_before(item, "tmdb_id", "douban_id")


def find_tmdb_hit(
    item: Dict[str, Any],
    token: str,
    debug_log: Optional[str] = None,
) -> tuple[Optional[Dict[str, Any]], str]:
    prefer = content_type_to_tmdb(item)
    imdb_id = normalize_imdb_id(item)
    tmdb_hit = None

    if imdb_id:
        try:
            tmdb_hit = tmdb_find_by_imdb(imdb_id, token, prefer)
        except Exception as exc:
            if debug_log:
                append_error_log(debug_log, f"IMDB_ERROR\t{imdb_id}\t{item.get('title') or item.get('id')}\t{exc}")
            tmdb_hit = None

    if not tmdb_hit:
        douban_val = item.get("douban_id")
        douban_id = str(douban_val).strip() if douban_val is not None else ""
        if douban_id:
            douban_info = douban_lookup(douban_id)
            if douban_info:
                title = (douban_info.get("title") or "").strip()
                year = (douban_info.get("year") or "").strip()
                if not title:
                    title = (item.get("title") or "").strip()
                try:
                    tmdb_hit = tmdb_search_by_title(title, token, prefer, year=year or None, language="zh-CN")
                    if not tmdb_hit:
                        tmdb_hit = tmdb_search_by_title(title, token, prefer, year=year or None, language="en-US")
                except Exception as exc:
                    if debug_log:
                        append_error_log(debug_log, f"TITLE_ERROR\t{title}\t{item.get('title') or item.get('id')}\t{exc}")
                    tmdb_hit = None

    if not tmdb_hit:
        title_candidates = []
        for key in ("title", "title_en"):
            val = (item.get(key) or "").strip()
            if val and val not in title_candidates:
                title_candidates.append(val)

        if title_candidates:
            for candidate in title_candidates:
                try:
                    tmdb_hit = tmdb_search_by_title(candidate, token, prefer, language="zh-CN")
                    if tmdb_hit:
                        break
                    tmdb_hit = tmdb_search_by_title(candidate, token, prefer, language="en-US")
                    if tmdb_hit:
                        break
                except Exception as exc:
                    if debug_log:
                        append_error_log(debug_log, f"TITLE_ERROR\t{candidate}\t{item.get('title') or item.get('id')}\t{exc}")
                    tmdb_hit = None

        if not tmdb_hit and title_candidates:
            alt_prefer = "tv" if prefer == "movie" else "movie"
            for candidate in title_candidates:
                try:
                    tmdb_hit = tmdb_search_by_title(candidate, token, alt_prefer, language="zh-CN")
                    if tmdb_hit:
                        prefer = alt_prefer
                        break
                    tmdb_hit = tmdb_search_by_title(candidate, token, alt_prefer, language="en-US")
                    if tmdb_hit:
                        prefer = alt_prefer
                        break
                except Exception as exc:
                    if debug_log:
                        append_error_log(debug_log, f"TITLE_ERROR\t{candidate}\t{item.get('title') or item.get('id')}\t{exc}")
                    tmdb_hit = None

    return tmdb_hit, prefer


def update_item(
    item: Dict[str, Any],
    token: str,
    debug_log: Optional[str] = None,
) -> tuple[bool, bool]:
    updated = False

    if item.get("original_title") and not item.get("title_en"):
        item["title_en"] = item.get("original_title")
        if isinstance(item, CommentedMap):
            ensure_title_en_position(item)
        updated = True
    if "original_title" in item:
        item.pop("original_title", None)
        updated = True

    tmdb_hit, prefer = find_tmdb_hit(item, token, debug_log=debug_log)

    if not tmdb_hit:
        return False, False

    tmdb_id = tmdb_hit.get("id")
    if tmdb_id and item.get("tmdb_id") != tmdb_id:
        item["tmdb_id"] = tmdb_id
        if isinstance(item, CommentedMap):
            ensure_tmdb_position(item)
        updated = True

    if tmdb_id:
        posters = tmdb_posters(tmdb_id, token, prefer)
        poster_zh = posters.get("zh")
        poster_en = posters.get("en")

        if poster_en and item.get("poster_en") != poster_en:
            item["poster_en"] = poster_en
            updated = True

        # poster = zh default, poster_en = en default (fallback to zh if needed)
        new_poster = poster_zh or poster_en
        if new_poster and item.get("poster") != new_poster:
            item["poster"] = new_poster
            updated = True
        if not item.get("poster_en") and poster_zh:
            item["poster_en"] = poster_zh
            updated = True

        # Ensure title_en is English
        try:
            title_en = tmdb_title_en(tmdb_id, token, prefer)
            if title_en and item.get("title_en") != title_en:
                item["title_en"] = title_en
                if isinstance(item, CommentedMap):
                    ensure_title_en_position(item)
                updated = True
        except Exception:
            pass

    return updated, True


def should_skip(item: Dict[str, Any]) -> bool:
    if item.get("tmdb_id") and item.get("poster") and item.get("poster_en") and item.get("title_en"):
        return True
    return False


def write_check_log(path: str, rows: List[str], append: bool = False) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "a" if append else "w"
    with open(path, mode, encoding="utf-8") as f:
        for row in rows:
            f.write(row + "\n")


def append_error_log(path: str, row: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(row + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token",
        help="TMDB Read Access Token",
        default=os.environ.get("TMDB_TOKEN")
        or "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0MTQ5NTQ5MzNlMWExMmQxODI0Y2VjMzQwZGY5ZGZjOSIsIm5iZiI6MTc2MzY3ODI1Ny40NTQwMDAyLCJzdWIiOiI2OTFmOTgzMTg2ZTgzMTg4ZTg1ZDVlMmMiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.omiM1gnvYcBMXhTIGukXocCBtqARyWfFEkwhchJxe5k",
    )
    parser.add_argument("--file", default="data/watched.yaml", help="Path to watched.yaml")
    parser.add_argument("--sleep", type=float, default=0.25, help="Sleep seconds between requests")
    parser.add_argument("--save-every", type=int, default=10, help="Write YAML every N items")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N items (0 = no limit)")
    parser.add_argument("--offset", type=int, default=0, help="Skip the first N items")
    parser.add_argument("--no-resume", action="store_true", help="Do not skip already-updated items")
    parser.add_argument("--check", action="store_true", help="Check matches without updating data")
    parser.add_argument(
        "--check-output",
        default="logs/tmdb_check_mismatches.txt",
        help="Output file for check mismatches",
    )
    parser.add_argument("--check-append", action="store_true", help="Append to check output file")
    parser.add_argument(
        "--error-log",
        default="logs/tmdb_errors.txt",
        help="Output file for update errors",
    )
    parser.add_argument(
        "--debug-match",
        action="store_true",
        help="Log match lookup errors for diagnostics",
    )
    parser.add_argument(
        "--debug-log",
        default="logs/tmdb_match_errors.txt",
        help="Output file for match lookup errors",
    )
    args = parser.parse_args()

    token = (args.token or "").strip()
    if not token:
        print("Missing TMDB token. Use --token or set TMDB_TOKEN.")
        return 1

    # Ensure logs exist when running updates
    if not args.check:
        write_check_log(args.error_log, [], append=False)
        if args.debug_match:
            write_check_log(args.debug_log, [], append=False)

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

    with open(args.file, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    watched = data.get("watched") or []
    total = len(watched)
    updated_count = 0
    pending_changes = 0

    if args.check:
        mismatches: List[str] = []
        processed = 0
        for idx, item in enumerate(watched, start=1):
            if args.offset and idx <= args.offset:
                continue
            if args.limit and processed >= args.limit:
                break
            title = item.get("title") or item.get("id")
            existing_tmdb = item.get("tmdb_id")
            try:
                tmdb_hit, _prefer = find_tmdb_hit(
                    item,
                    token,
                    debug_log=(args.debug_log if args.debug_match else None),
                )
            except Exception as exc:
                mismatches.append(f"[{idx}] ERROR\t{title}\t{existing_tmdb}\t{exc}")
                processed += 1
                continue

            if tmdb_hit:
                new_tmdb = tmdb_hit.get("id")
                if existing_tmdb and new_tmdb and str(existing_tmdb) != str(new_tmdb):
                    mismatches.append(f"[{idx}] MISMATCH\t{title}\t{existing_tmdb}\t{new_tmdb}")
            else:
                if existing_tmdb:
                    mismatches.append(f"[{idx}] NO_MATCH\t{title}\t{existing_tmdb}\t")

            processed += 1
            if args.sleep:
                time.sleep(args.sleep)

            if processed % 10 == 0:
                print(f"Checked {processed}/{args.limit or total}...")

        write_check_log(args.check_output, mismatches, append=args.check_append)
        print(f"Check complete. Mismatches: {len(mismatches)} -> {args.check_output}")
        return 0

    try:
        processed = 0
        for idx, item in enumerate(watched, start=1):
            if args.offset and idx <= args.offset:
                continue
            if args.limit and processed >= args.limit:
                break
            title = item.get("title") or item.get("id")
            if not args.no_resume and should_skip(item):
                print(f"[{idx}/{total}] Skipped: {title}")
                continue
            try:
                changed, matched = update_item(
                    item,
                    token,
                    debug_log=(args.debug_log if args.debug_match else None),
                )
                if changed:
                    updated_count += 1
                    pending_changes += 1
                    print(f"[{idx}/{total}] Updated: {title}")
                elif matched:
                    print(f"[{idx}/{total}] No change: {title}")
                else:
                    print(f"[{idx}/{total}] No match: {title}")
            except Exception as exc:
                print(f"[{idx}/{total}] Error: {title} -> {exc}")
                append_error_log(args.error_log, f"[{idx}] {title}\t{exc}")
            processed += 1
            if args.save_every > 0 and pending_changes > 0 and idx % args.save_every == 0:
                with open(args.file, "w", encoding="utf-8") as f:
                    yaml.dump(data, f)
                pending_changes = 0
            time.sleep(args.sleep)
    except KeyboardInterrupt:
        print("Interrupted. Saving progress...")
    finally:
        if pending_changes > 0:
            with open(args.file, "w", encoding="utf-8") as f:
                yaml.dump(data, f)

    print(f"Done. Updated {updated_count}/{total} items.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
