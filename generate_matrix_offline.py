#!/usr/bin/env python3

import json
import os
from packaging.version import Version

MONGO_VERSIONS = ["5", "6", "7", "8"]

versions = [Version(version) for version in MONGO_VERSIONS]
min_v = Version(os.getenv("GHA_INPUT_MIN") or "4.0")
max_v_raw = os.getenv("GHA_INPUT_MAX")
exclude = {v.strip() for v in os.getenv("GHA_INPUT_EXCLUDE", "").split(",") if v.strip()}
max_v = Version(max_v_raw) if max_v_raw else max(versions)

filtered = [
    str(version) for version in MONGO_VERSIONS
    if min_v <= Version(version) <= max_v and str(version) not in exclude
]

print(json.dumps(filtered))
