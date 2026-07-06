import json
from datetime import datetime, timezone

from apify import Actor
from crawlee.crawlers import Router

router = Router[dict]()


@router.handler('search')
async def handle_search(context) -> None:
    response = await context.get_current_page().response_async()
    html = await response.text_async()

    from selectolax.parser import HTMLParser
    doc = HTMLParser(html)
    links = []
    seen = set()
    for node in doc.tags('a'):
        href = node.attributes.get('href', '')
        if '/app/' in href:
            app_id = href.split('/app/')[1].split('/')[0]
            if app_id not in seen:
                seen.add(app_id)
                links.append(f'https://store.steampowered.com/app/{app_id}')

    for url in links[:20]:
        await context.add_requests([{'url': url, 'userData': {'handler': 'app'}}])

    try:
        await Actor.charge('store_snapshot', {
            'crawledAt': datetime.now(timezone.utc).isoformat(),
            'url': response.url,
            'enqueuedApps': len(links[:20]),
        })
    except RuntimeError:
        pass


@router.handler('app')
async def handle_app(context) -> None:
    response = await context.get_current_page().response_async()
    html = await response.text_async()

    from selectolax.parser import HTMLParser
    doc = HTMLParser(html)

    title_node = doc.css_first('.apphub_AppName')
    title = title_node.text().strip() if title_node else ''

    price_node = doc.css_first('.game_purchase_price, .discount_final_price')
    price = price_node.text().strip() if price_node else ''

    discount_node = doc.css_first('.discount_pct')
    discount = discount_node.text().strip() if discount_node else '0%'

    released_node = doc.css_first('.release_date .date')
    released = released_node.text().strip() if released_node else ''

    platforms = []
    for platform in doc.css('.platform_img'):
        cls = platform.attributes.get('class', '')
        if 'win' in cls:
            platforms.append('Windows')
        if 'mac' in cls:
            platforms.append('Mac')
        if 'linux' in cls:
            platforms.append('Linux')

    item = {
        'title': title,
        'currentPrice': price,
        'discountPercent': discount,
        'releaseDate': released,
        'platforms': ', '.join(platforms),
        'appUrl': response.url,
        'detectedAt': datetime.now(timezone.utc).isoformat(),
    }

    dataset = await Actor.open_dataset()
    await dataset.push_data(item)

    try:
        await Actor.charge('game_record', item)
    except RuntimeError:
        pass
