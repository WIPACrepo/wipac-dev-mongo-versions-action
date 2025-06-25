#!/usr/bin/env python3

import json
import os
from packaging.version import Version, InvalidVersion
import requests
import time

# Interpret a string as a boolean-like flag
def is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}

omit_rc = is_truthy(os.getenv("GHA_INPUT_OMIT_RC"))
min_v = Version(os.getenv("GHA_INPUT_MIN") or "4.0")
max_v_raw = os.getenv("GHA_INPUT_MAX")
exclude = {v.strip() for v in os.getenv("GHA_INPUT_EXCLUDE", "").split(",") if v.strip()}

# Fetch all tags from Docker Hub (paginated)
tags = []
url = "https://registry.hub.docker.com/v2/repositories/library/mongo/tags?page_size=100"
while url:
    time.sleep(1)
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    tags += [tag["name"] for tag in data["results"]]
    url = data.get("next")

# Keep only versions that look like 4.4, 6.0.3, 8.0.0-rc4, etc.
def parse_mongo_tag(tag):
    try:
        return Version(tag.strip())
    except InvalidVersion:
        return None

parsed_versions = [parse_mongo_tag(t) for t in tags]
parsed_versions = [v for v in parsed_versions if v and v.release and isinstance(v.release, tuple)]

# Group versions by major.minor (ignore patch)
grouped = {}
latest_rc = None

for v in parsed_versions:
    key = f"{v.major}.{v.minor}"

    if v.is_prerelease:
        if latest_rc is None or v > latest_rc:
            latest_rc = v
        continue

    if key not in grouped:
        grouped[key] = v
        continue

    if v > grouped[key]:
        grouped[key] = v

# Add latest prerelease, if not already included
if latest_rc and not omit_rc:
    key = f"{latest_rc.major}.{latest_rc.minor}"
    if key not in grouped:
        grouped[latest_rc] = latest_rc

# Determine max_v
max_v = Version(max_v_raw) if max_v_raw else max(grouped.values())

# Final filter
filtered = [
    str(key) for key, v in sorted(grouped.items(), key=lambda x: Version(x[0]))
    if min_v <= Version(key) <= max_v and key not in exclude
]

print(json.dumps(filtered))
