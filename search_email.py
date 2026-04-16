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

    "escort_sites": [
        "loquosex.com", "destacamos.com", "publicontactos.com",
        "choosescorts.com", "slumi.com", "nuevapasion.com",
        "skokka.com", "milpasiones.com", "mileroticos.com",
        "oklute.com", "mundosexanuncio.com", "milescorts.com",
        "eurogirlsescort.com", "sexjobs.es", "publihot.com",
        "pasion.com", "putas69", "happyescorts",
        "nuevoloquo", "citaspasion", "erosguia", "agenda69",
        "madrid69", "red-life", "goputas"
    ],

    "forums": [
        "forocoches", "spalumi", "foro", "reddit"
    ]
}


def detect_platform(link, title):
    text = (link + " " + title).lower()
    detected = set()

    for category, patterns in PLATFORMS.items():
        for p in patterns:
            if p in text:
                detected.add(category)

    return detected


def contains_email(text, email):
    # only keep results where email appears literally
    return email.lower() in text.lower()


def is_noise(link):
    link = link.lower()

    noise_patterns = [
        "categoria", "tag", "listado",
        "page=", "buscar", "search",
        "/category/", "/tags/",
        "/page/", "?p="
    ]

    return any(n in link for n in noise_patterns)


def score_result(title, link):
    # scoring only for ordering, not filtering
    score = 0
    t = title.lower()

    if "escort" in t or "contactos" in t:
        score += 2

    if "masajes" in t:
        score += 2

    if any(x in link for x in [".html", "details"]):
        score += 1

    return score


# google fallback
def google_search(query):
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


def search_email(email):

    queries = list(set([

        f'"{email}"',

        f'"{email}" contactos',
        f'"{email}" escort',
        f'"{email}" masajes',

        # escort sites
        f'"{email}" site:loquosex.com',
        f'"{email}" site:destacamos.com',
        f'"{email}" site:mileroticos.com',
        f'"{email}" site:skokka.com',
        f'"{email}" site:slumi.com',
        f'"{email}" site:pasion.com',

        # forums
        f'"{email}" site:spalumi.com',
        f'"{email}" foro',

        # socials 
        f'"{email}" instagram',
        f'"{email}" facebook',
        f'"{email}" twitter',
    ]))

    seen_links = set()
    all_results = []
    platform_hits = {k: False for k in PLATFORMS.keys()}

    print(f"\n[+] Engine in use: {ENGINE}")
    print("\n[+] Starting email OSINT search...\n")

    with DDGS() as ddgs:
        for query in queries:
            print(f"[+] Searching: {query}")

            try:
                results = ddgs.text(query, max_results=10)
            except:
                results = []

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

                text = (link + " " + title)

                # Hard filter
                if not contains_email(text, email):
                    continue

                detected = detect_platform(link, title)

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
                    "score": score
                })

    print("\n[+] Summary:\n")

    for p, v in platform_hits.items():
        print(f"{p}: {'✔' if v else '✘'}")

    all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)

    with open(f"email_{email}.json", "w") as f:
        json.dump({
            "email": email,
            "platforms_detected": platform_hits,
            "results": all_results
        }, f, indent=4)

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="Email to search")

    args = parser.parse_args()

    if args.email:
        search_email(args.email)
    else:
        print("[-] Provide an email with --email")
