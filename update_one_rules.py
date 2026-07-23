#!/usr/bin/env python3
"""Generate full One rule sets for Karing and Mihomo/OpenClash.

Source: https://github.com/ignaciocastro/a-dove-is-dumb
No third-party Python packages are required.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SOURCES = (
    "https://raw.githubusercontent.com/ignaciocastro/a-dove-is-dumb/main/clash.yaml",
    "https://cdn.jsdelivr.net/gh/ignaciocastro/a-dove-is-dumb@latest/clash.yaml",
    "https://fastly.jsdelivr.net/gh/ignaciocastro/a-dove-is-dumb@latest/clash.yaml",
)

DOMAIN_RE = re.compile(r"^\s*-\s*DOMAIN,([^,\s]+)\s*$", re.IGNORECASE)
OUTPUT_DIR = Path(__file__).resolve().parent


def download_source() -> tuple[str, str]:
    errors: list[str] = []
    headers = {
        "User-Agent": "Mozilla/5.0 One-Rules-Updater/1.0",
        "Accept": "text/plain,*/*",
    }
    for url in SOURCES:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as response:
                text = response.read().decode("utf-8-sig")
            if "payload:" not in text or "DOMAIN," not in text:
                raise ValueError("downloaded content is not a Clash rule provider")
            return url, text
        except (urllib.error.URLError, TimeoutError, ValueError, UnicodeError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("All upstream downloads failed:\n" + "\n".join(errors))


def parse_domains(text: str) -> list[str]:
    domains: list[str] = []
    seen: set[str] = set()

    for raw_line in text.splitlines():
        match = DOMAIN_RE.match(raw_line)
        if not match:
            continue
        domain = match.group(1).strip().lower().rstrip(".")
        if not domain or domain in seen:
            continue
        if any(ch.isspace() for ch in domain) or "/" in domain:
            raise ValueError(f"Invalid domain in upstream: {domain!r}")
        seen.add(domain)
        domains.append(domain)

    # The list has thousands of entries. Fail loudly instead of silently
    # publishing a truncated error page or an incomplete download.
    if len(domains) < 1000:
        raise RuntimeError(
            f"Only parsed {len(domains)} domains; refusing to publish a partial ruleset"
        )
    return domains


def write_karing_json(domains: list[str]) -> Path:
    # sing-box source rule-set format; Karing accepts remote .json rule sets.
    data = {
        "version": 3,
        "rules": [
            {
                "domain": domains,
            }
        ],
    }
    path = OUTPUT_DIR / "one-block.json"
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def write_mihomo_yaml(domains: list[str]) -> Path:
    # Classical Mihomo rule-provider format. Use behavior: classical, format: yaml.
    lines = [
        "# Full One blocklist",
        "# Generated from ignaciocastro/a-dove-is-dumb",
        "payload:",
    ]
    lines.extend(f"  - DOMAIN,{domain}" for domain in domains)
    path = OUTPUT_DIR / "one-block.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def write_mihomo_text(domains: list[str]) -> Path:
    # Optional Mihomo text provider format.
    path = OUTPUT_DIR / "one-block.txt"
    path.write_text(
        "\n".join(f"DOMAIN,{domain}" for domain in domains) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def write_metadata(source_url: str, domains: list[str]) -> Path:
    data = {
        "source": source_url,
        "upstream_repository": "https://github.com/ignaciocastro/a-dove-is-dumb",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "domain_count": len(domains),
        "outputs": {
            "karing": "one-block.json",
            "mihomo_openclash_yaml": "one-block.yaml",
            "mihomo_openclash_text": "one-block.txt",
        },
    }
    path = OUTPUT_DIR / "metadata.json"
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def main() -> int:
    try:
        source_url, text = download_source()
        domains = parse_domains(text)
        outputs = [
            write_karing_json(domains),
            write_mihomo_yaml(domains),
            write_mihomo_text(domains),
            write_metadata(source_url, domains),
        ]
    except Exception as exc:  # noqa: BLE001 - CLI should present a clean error
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Source: {source_url}")
    print(f"Domains: {len(domains)}")
    for path in outputs:
        print(f"Generated: {path.name} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
