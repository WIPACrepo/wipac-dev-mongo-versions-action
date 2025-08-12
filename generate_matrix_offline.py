#!/usr/bin/env python3

import json
import os
from packaging.version import Version, InvalidVersion

MONGO_VERSIONS = ["5.0", "6.0", "7.0", "8.0"]

min_v = Version(os.getenv("GHA_INPUT_MIN") or "4.0")
max_v_raw = os.getenv("GHA_INPUT_MAX")
exclude = {v.strip() for v in os.getenv("GHA_INPUT_EXCLUDE", "").split(",") if v.strip()}

max_v = Version(max_v_raw) if max_v_raw else max(MONGO_VERSIONS.values())

filtered = [
    str(version) for version in MONGO_VERSIONS
    if min_v <= Version(version) <= max_v and version not in exclude
]

print(json.dumps(filtered))
