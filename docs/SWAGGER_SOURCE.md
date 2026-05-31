# NocoDB OpenAPI Specifications — Source & Provenance

The OpenAPI/Swagger specs in this directory are **vendored copies** of the
official NocoDB specifications, kept for reference and migration analysis only.

## Files

| File | Title | Paths | Description |
|------|-------|------:|-------------|
| `swagger-v2.json` | NocoDB v2 | 112 | Official NocoDB **v2** OpenAPI spec (data + meta combined) |
| `swagger-v3.json` | NocoDB v3 | 51 | Official NocoDB **v3** OpenAPI spec (data + meta combined) |
| `swagger-v3-validation-patch.json` | — | — | Upstream `components`-only validation patch applied on top of v3 |

## Provenance

- **Source:** [`nocodb/nocodb`](https://github.com/nocodb/nocodb) — `packages/nocodb/src/schema/`
- **Pinned commit:** `a9f8eb1e5934242177dd577fa6bfb7c2b785c316` (branch `develop`, 2026-05-29)
- **Raw URL pattern:**
  `https://raw.githubusercontent.com/nocodb/nocodb/<commit>/packages/nocodb/src/schema/<file>`

To refresh, re-download the three files from the same path at a newer commit
and update the pinned commit above.

## ⚠️ Important caveats

1. **`develop` runs ahead of releases.** These specs track the upstream
   `develop` branch and may describe endpoints that a given NocoDB *release*
   does not yet expose. Example: `swagger-v3.json` lists v3 webhook/hook paths
   (`.../tables/{tableId}/hooks`), but a deployed release (verified against
   `releaseVersion 2026.05.2`) still answers those v3 hook paths with HTTP 404.
2. **Always verify against the deployed instance.** The authoritative behavior
   is what the running NocoDB server actually does, not the spec.
3. **Do not derive client code directly from these files.** The previous,
   incomplete snapshots (now removed) caused several wrong v3 conclusions
   (sort/where format, attachment upload, webhooks). The client's v3 behavior
   in this library was corrected by **live testing** against a running instance
   — keep doing that.

## History

These replace four earlier, mislabeled snapshots
(`nocodb-openapi-{data,meta}.json` and their `-v3` variants) that together held
only 19 paths, had `data`/`meta` swapped, and diverged from the real API.
