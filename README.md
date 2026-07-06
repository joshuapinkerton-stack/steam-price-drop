# Steam Price Drop Tracker

Track Steam store prices, discounts, and release dates for top sellers and curated game lists.

## Example input

{ "searchUrl": "https://store.steampowered.com/search/?filter=topsellers", "maxPages": 3 }

## Output events

| Event | Shape |
|-------|-------|
| `store_snapshot` | Crawl metadata |
| `game_record` | Title, price, discount, platforms, app URL |

## Pricing

Pay-per-Event: $0.04/game_record + $0.08/store_snapshot.
