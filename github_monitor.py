import os
import requests
from bs4 import BeautifulSoup

GITHUB_API = "https://api.github.com"
TRENDING_URL = "https://github.com/trending"


def _headers():
    token = os.getenv("GITHUB_TOKEN", "")
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def get_trending_repos(languages: list[str]) -> list[dict]:
    """Scrape GitHub trending page. Returns list of repo dicts."""
    results = []
    langs_to_check = languages if languages else [None]

    for lang in langs_to_check:
        url = TRENDING_URL
        params = {"since": "daily"}
        if lang:
            params["l"] = lang
        try:
            resp = requests.get(url, params=params, timeout=15,
                                headers={"User-Agent": "github-trend-agent/1.0"})
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  [github] trending fetch failed for lang={lang}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for article in soup.select("article.Box-row"):
            name_el = article.select_one("h2 a")
            if not name_el:
                continue
            full_name = name_el.get("href", "").strip("/")
            desc_el = article.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""
            lang_el = article.select_one("[itemprop='programmingLanguage']")
            repo_lang = lang_el.get_text(strip=True) if lang_el else ""
            stars_el = article.select_one("a[href$='/stargazers']")
            stars = stars_el.get_text(strip=True).replace(",", "") if stars_el else "0"
            stars_today_el = article.select_one("span.d-inline-block.float-sm-right")
            stars_today = stars_today_el.get_text(strip=True) if stars_today_el else ""

            results.append({
                "full_name": full_name,
                "url": f"https://github.com/{full_name}",
                "description": description,
                "language": repo_lang,
                "stars": stars,
                "stars_today": stars_today,
            })

    seen = set()
    deduped = []
    for r in results:
        if r["full_name"] not in seen:
            seen.add(r["full_name"])
            deduped.append(r)
    return deduped


def get_hot_issues(repos: list[dict], min_comments: int) -> list[dict]:
    """For each trending repo, fetch recently-active issues with many comments."""
    hot = []
    for repo in repos[:15]:  # cap to avoid rate limits
        full_name = repo["full_name"]
        try:
            resp = requests.get(
                f"{GITHUB_API}/repos/{full_name}/issues",
                headers=_headers(),
                params={
                    "state": "open",
                    "sort": "comments",
                    "direction": "desc",
                    "per_page": 5,
                },
                timeout=10,
            )
            if resp.status_code == 403:
                print("  [github] rate limited on issues API")
                break
            if resp.status_code != 200:
                continue
            for issue in resp.json():
                if issue.get("pull_request"):
                    continue
                if issue.get("comments", 0) < min_comments:
                    continue
                hot.append({
                    "repo": full_name,
                    "repo_url": repo["url"],
                    "title": issue["title"],
                    "url": issue["html_url"],
                    "comments": issue["comments"],
                    "created_at": issue["created_at"],
                    "labels": [l["name"] for l in issue.get("labels", [])],
                })
        except requests.RequestException as e:
            print(f"  [github] issues fetch failed for {full_name}: {e}")
            continue

    hot.sort(key=lambda x: x["comments"], reverse=True)
    return hot[:20]
