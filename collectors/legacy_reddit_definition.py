                                                                                   
import time
import requests
import pandas as pd
from datetime import datetime,timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from crypto_lexicon import CRYPTO_LEXICON

BASE_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"

SUBREDDIT = "Bitcoin"

LIMIT = 100

SLEEP_SECONDS = 0.7

PAGE_SLEEP_SECONDS = 0.2

MAX_RETRIES = 3

def build_analyzer():
    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(CRYPTO_LEXICON)
    return analyzer

def score_text(analyzer, text):
    if not text:
        return None
    return analyzer.polarity_scores(text)["compound"]

def request_posts(after_ts, before_ts, limit=LIMIT):
                                                                     
                                                                 
    params = {
        "subreddit": SUBREDDIT,
        "after": after_ts,
        "before": before_ts,
        "limit": limit,
                                                                           
                                                                 
        "fields": "title,selftext,created_utc",
    }

    headers = {
        "User-Agent": "thesis-research/1.0"
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                BASE_URL,
                params=params,
                headers=headers,
                timeout=30
            )

            if response.status_code == 429:
                print("Rate limit hit. Sleeping 60 seconds...")
                time.sleep(60)
                continue

            response.raise_for_status()
            return response.json().get("data", [])

        except Exception as e:
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            time.sleep(5)

    return None

def score_posts_for_day(analyzer, day):
    day_start = int(day.timestamp())
    day_end = int((day + timedelta(days=1)).timestamp())

    scores = []
    before_ts = day_end

    while True:
        posts = request_posts(after_ts=day_start, before_ts=before_ts)

        if posts is None:
            return None                                                        

        if len(posts) == 0:
            break

        for post in posts:
            text = f"{post.get('title', '') or ''} {post.get('selftext', '') or ''}"
            s = score_text(analyzer, text)
            if s is not None:
                scores.append(s)

        if len(posts) < LIMIT:
            break

        oldest_created = min(post.get("created_utc", before_ts) for post in posts)
        new_before_ts = oldest_created - 1

        if new_before_ts >= before_ts:
            break

        before_ts = new_before_ts
        time.sleep(PAGE_SLEEP_SECONDS)

    if not scores:
        return None
    return sum(scores) / len(scores)
