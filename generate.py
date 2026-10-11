import feedparser
import json
import os
import re
from datetime import datetime, timezone, timedelta
from feedgen.feed import FeedGenerator

HK_TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(HK_TZ).strftime('%Y-%m-%d')
DATA_DIR = 'data'

# === 1. 你嘅 RSS 來源 ===
FEEDS = {
    '科技': [
        'https://techcrunch.com/feed/',
        'https://www.theverge.com/rss/index.xml',
    ],
    '商業': [
        'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    ],
    '宇宙': [
        'https://www.nasa.gov/rss/dyn/breaking_news.rss',
    ],
    '時事': [
        'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    ],
}

# === 2. 關鍵詞規則（用嚟抽 tag）===
KEYWORDS = [
    'AI', '晶片', '美股', '港股', '航天', '火箭', '衛星',
    '通脹', '減息', '電動車', '半導體', '量子', '氣候',
]

def clean(text):
    text = re.sub(r'<[^>]+>', '', text or '')
    return text.strip()[:300]

def extract_keywords(title, summary):
    text = f"{title} {summary}".lower()
    return [k for k in KEYWORDS if k.lower() in text]

def fetch_feeds():
    items = []
    for category, urls in FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:15]:
                    title = clean(entry.get('title', ''))
                    summary = clean(entry.get('summary', ''))
                    items.append({
                        'title': title,
                        'url': entry.get('link', ''),
                        'summary': summary,
                        'category': category,
                        'source': feed.feed.get('title', url),
                        'keywords': extract_keywords(title, summary),
                        'date': TODAY,
                    })
            except Exception as e:
                print(f'[錯誤] {url}: {e}')
    # 去重
    seen, unique = set(), []
    for it in items:
        if it['url'] and it['url'] not in seen:
            seen.add(it['url'])
            unique.append(it)
    return unique

def load_json(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_index():
    path = f'{DATA_DIR}/index.json'
    idx = load_json(path, {'dates': [], 'lastUpdated': ''})
    if TODAY not in idx['dates']:
        idx['dates'].insert(0, TODAY)
    idx['dates'] = sorted(set(idx['dates']), reverse=True)
    idx['lastUpdated'] = datetime.now(HK_TZ).isoformat()
    save_json(path, idx)

def update_search_index(items):
    path = f'{DATA_DIR}/search-index.json'
    idx = load_json(path, [])
    existing = {i['url'] for i in idx}
    for it in items:
        if it['url'] not in existing:
            idx.append({
                'date': it['date'],
                'title': it['title'],
                'keywords': it['keywords'],
                'url': it['url'],
                'category': it['category'],
            })
    save_json(path, idx)

def update_keywords(items):
    path = f'{DATA_DIR}/keywords.json'
    kw = load_json(path, {})
    for it in items:
        for k in it['keywords']:
            kw.setdefault(k, {})
            kw[k][TODAY] = kw[k].get(TODAY, 0) + 1
    # 只保留近 90 日
    cutoff = (datetime.now(HK_TZ) - timedelta(days=90)).strftime('%Y-%m-%d')
    for k in kw:
        kw[k] = {d: c for d, c in kw[k].items() if d >= cutoff}
    save_json(path, kw)

def build_rss(items):
    fg = FeedGenerator()
    fg.title('我嘅每日話題')
    fg.link(href='https://你的用戶名.github.io/倉庫名/', rel='alternate')
    fg.description('每日精選時事、商業、股市、宇宙、科技話題')
    for it in items[:30]:
        fe = fg.add_entry()
        fe.title(it['title'])
        fe.link(href=it['url'])
        fe.description(it['summary'])
        fe.category(term=it['category'])
        fe.pubDate(datetime.now(HK_TZ))
    fg.rss_file('feed.xml')

def main():
    items = fetch_feeds()
    print(f'抓到 {len(items)} 條')
    save_json(f'{DATA_DIR}/{TODAY}.json', {'date': TODAY, 'items': items})
    update_index()
    update_search_index(items)
    update_keywords(items)
    build_rss(items)

if __name__ == '__main__':
    main()
