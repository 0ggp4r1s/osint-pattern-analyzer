import json
import argparse
import requests
from bs4 import BeautifulSoup

# search engine fallback
try:
    from ddgs import DDGS
    ENGINE = "ddgs"
except:
    from duckduckgo_search import DDGS
    ENGINE = "duckduckgo"


# platform classification
PLATFORMS = {
    "telegram": ["t.me", "telegram"],

    "social": [
        "instagram.com",
        "twitter.com", "x.com",
        "facebook.com"
    ],

    "dating": [
        "tinder", "badoo", "bumble", "hinge", "meetic",
        "okcupid", "happn", "lovoo", "adoptauntio", "grindr"
    ],

    "sugar": [
        "seeking", "mysugardaddy", "secretbenefits",
        "sugardaddymeet", "sudy", "sugardaddy.com", "glambu"
    ],

    "adult_creator": [
        "onlyfans", "fansly", "fanvue", "mym", "loyalfans",
        "fancentro", "justforfans", "manyvids",
        "patreon", "exclu", "unlockd", "avnstars", "my.club"
    ],

    "escort_sites": [
        "loquosex.com", "destacamos.com", "publicontactos.com",
        "choosescorts.com", "slumi.com", "nuevapasion.com",
        "skokka.com", "milpasiones.com", "mileroticos.com",
        "oklute.com", "mundosexanuncio.com", "milescorts.com",
        "eurogirlsescort.com", "sexjobs.es", "publihot.com",
        "pasion.com", "putas69", "happyescorts"
    ],

    "forums": [
        "forocoches", "spalumi", "reddit"
    ]
}


def detect_platform(link, title):
    # detect platform based on link + title context
    text = (link + " " + title).lower()
    detected = set()

    for category, patterns in PLATFORMS.items():
        for p in patterns:
            if p in text:
                detected.add(category)

    return detected


def is_noise(link):
    # remove obvious listing/category pages but allow facebook
    link = link.lower()

    if "facebook.com" in link:
        return False

    noise_patterns = [
        "categoria", "tag", "listado",
        "page=", "buscar", "search",
        "/category/", "/tags/",
        "/page/", "?p="
    ]

    return any(n in link for n in noise_patterns)


def is_exact_username_match(link, username):
    # strict match in URL
    return f"/{username.lower()}" in link.lower()


def score_result(title, link):
    # soft scoring, only used for ordering results
    score = 0
    t = title.lower()

    if "masajes" in t:
        score += 2

    if "escort" in t or "contactos" in t:
        score += 2

    if "facebook.com" in link:
        score += 3

    if "x.com" in link or "twitter.com" in link:
        score += 2

    if "t.me" in link:
        score += 3

    return score


def google_search(query):
    # basic google scraping fallback when DDG returns nothing
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.google.com/search?q={query}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for a in soup.find_all("a"):
        href = a.get("href")

        if href and "/url?q=" in href:
            link = href.split("/url?q=")[1].split("&")[0]

            results.append({
                "href": link,
                "title": link
            })

    return results


def search_username(username):

    # expanded queries
    queries = list(set([
        f'"{username}"',

        f'"{username}" telegram',
        f'"{username}" site:t.me',

        f'"{username}" instagram',

        f'"{username}" twitter',
        f'"{username}" x.com',
        f'"{username}" site:twitter.com',
        f'"{username}" site:x.com',

        # facebook boosted queries
        f'"{username}" facebook',
        f'"{username}" "facebook"',
        f'"{username}" "fb"',
        f'site:facebook.com "{username}"',
        f'site:m.facebook.com "{username}"',

        f'"{username}" escort',
        f'"{username}" contactos',
        f'"{username}" masajes',

        f'"{username}" site:mileroticos.com',
        f'"{username}" site:slumi.com',
        f'"{username}" site:skokka.com'
    ]))

    seen_links = set()
    all_results = []

    platform_hits = {k: False for k in PLATFORMS.keys()}

    print(f"\n[+] Engine in use: {ENGINE}")
    print("\n[+] Starting username OSINT search...\n")

    with DDGS() as ddgs:
        for query in queries:
            print(f"[+] Searching: {query}")

            try:
                results = ddgs.text(query, max_results=10)
            except:
                results = []

            # fallback to google if no results
            if not results:
                print(f"[!] Google fallback: {query}")
                results = google_search(query)

            for r in results:
                link = r.get("href")
                title = r.get("title") or ""

                if not link:
                    continue

                if link in seen_links:
                    continue

                if "duckduckgo.com" in link:
                    continue

                if is_noise(link):
                    continue

                detected = detect_platform(link, title)
                exact_match = is_exact_username_match(link, username)

                # --- FACEBOOK FIX ---
                # facebook is poorly indexed, so dont filter it aggressively
                if "facebook.com" in link:
                    seen_links.add(link)
                    platform_hits["social"] = True

                    score = score_result(title, link)

                    print(f"[+] {title}")
                    print(link, "\n")

                    all_results.append({
                        "query": query,
                        "title": title,
                        "link": link,
                        "categories": ["social"],
                        "score": score,
                        "exact_match": exact_match
                    })
                    continue

                # --- MAIN FILTER LOGIC ---

                if "social" in detected:
                    pass

                elif "escort_sites" in detected:
                    pass

                elif "forums" in detected:
                    pass

                elif exact_match:
                    pass

                else:
                    continue

                seen_links.add(link)

                for d in detected:
                    platform_hits[d] = True

                score = score_result(title, link)

                print(f"[+] {title}")
                print(link, "\n")

                all_results.append({
                    "query": query,
                    "title": title,
                    "link": link,
                    "categories": list(detected),
                    "score": score,
                    "exact_match": exact_match
                })

    print("\n[+] Summary:\n")

    for p, v in platform_hits.items():
        print(f"{p}: {'✔' if v else '✘'}")

    all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)

    with open(f"username_{username}.json", "w") as f:
        json.dump({
            "username": username,
            "platforms_detected": platform_hits,
            "results": all_results
        }, f, indent=4)

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="Username to search")

    args = parser.parse_args()

    if args.username:
        search_username(args.username)
    else:
        print("[-] Provide a username with --username")
