"""
Automated Publisher for DEV Community Article
Uses the official DEV.to REST API (https://dev.to/api/articles)
"""

import os
import sys
import json
import urllib.request
import urllib.error


def publish_article(api_key: str):
    article_path = os.path.join(os.path.dirname(__file__), "..", "submission", "dev_article.md")
    with open(article_path, "r", encoding="utf-8") as f:
        markdown_body = f.read()

    # The DEV API endpoint accepts body_markdown containing full frontmatter
    payload = {
        "article": {
            "title": "The Missing Piece: Why AI Models Hallucinate Answers When They Should Abstain",
            "published": True,
            "body_markdown": markdown_body,
            "tags": ["devchallenge", "kagglechallenge", "ai", "machinelearning"],
            "main_image": "https://raw.githubusercontent.com/Shreyansh00987/Missing-Piece/main/assets/cover/missing_piece_cover.jpg"
        }
    }

    url = "https://dev.to/api/articles"
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "api-key": api_key.strip(),
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MissingPiece/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            article_url = data.get("url")
            print(f"SUCCESS: Article published successfully!")
            print(f"Live Article URL: {article_url}")
            return article_url
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Details: {err_msg}")
        sys.exit(1)
    except Exception as e:
        print(f"Error publishing article: {e}")
        sys.exit(1)


if __name__ == "__main__":
    key = os.environ.get("DEV_API_KEY")
    if len(sys.argv) > 1:
        key = sys.argv[1]

    if not key:
        print("Error: No DEV API key provided. Pass as argument or set DEV_API_KEY.")
        sys.exit(1)

    publish_article(key)
