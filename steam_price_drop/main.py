import json
from datetime import datetime, timezone

from apify import Actor
from crawlee.crawlers import CheerioCrawler
from crawlee import router

from .routes import router as steam_router


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        search_url = actor_input.get(
            'searchUrl',
            'https://store.steampowered.com/search/?filter=topsellers',
        )
        max_pages = int(actor_input.get('maxPages', 3))

        requests = [
            {'url': f'{search_url}&page={page}', 'userData': {'handler': 'search'}}
            for page in range(1, max_pages + 1)
        ]

        crawler = CheerioCrawler(
            max_requests_per_crawl=max_pages + 5,
            max_request_retries=4,
            request_handler=steam_router,
        )

        await crawler.run(requests)

        dataset = await Actor.open_dataset()
        await dataset.push_data({
            'type': 'crawl_run_meta',
            'crawledAt': datetime.now(timezone.utc).isoformat(),
            'searchUrl': search_url,
            'maxPages': max_pages,
        })

        try:
            await Actor.charge('store_snapshot', {
                'crawledAt': datetime.now(timezone.utc).isoformat(),
                'searchUrl': search_url,
            })
        except RuntimeError:
            pass

        Actor.log.info(f'Steam crawl completed: {max_pages} pages.')
