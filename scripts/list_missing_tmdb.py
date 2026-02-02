from ruamel.yaml import YAML
import os

yaml = YAML(typ="rt")
with open("data/watched.yaml", "r", encoding="utf-8") as f:
    data = yaml.load(f)

rows = []
for idx, item in enumerate(data.get("watched") or [], start=1):
    if not isinstance(item, dict):
        continue
    if item.get("tmdb_id") in (None, ""):
        title = item.get("title") or item.get("id") or ""
        imdb_id = item.get("imdb_id") or ""
        douban_id = item.get("douban_id") or ""
        rows.append(f"[{idx}]\t{title}\t{imdb_id}\t{douban_id}")

log_path = os.path.join("logs", "tmdb_errors.txt")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
with open(log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(rows))

print(f"No-tmdb_id items: {len(rows)} -> {log_path}")
