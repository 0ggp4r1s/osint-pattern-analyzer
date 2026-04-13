from ddgs import DDGS
import json
import argparse


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


def is_relevant_result(link, title):
    text = (link + " " + title).lower()

    # avoid generic pages
    if any(x in text for x in [
        "categoria", "tag", "listado", "page=", "search"
    ]):
        return False

    return True


def search_username(username):

    queries = [
        f'"{username}"',
        f'"{username}" telegram',
        f'"{username}" site:t.me',
        f'"{username}" instagram',
        f'"{username}" twitter',
        f'"{username}" onlyfans',
        f'"{username}" escort',
        f'"{username}" contactos',

        # escort-focused
        f'"{username}" site:mileroticos.com',
        f'"{username}" site:slumi.com',
        f'"{username}" site:skokka.com',
        f'"{username}" site:loquosex.com'
    ]

    queries = list(set(queries))

    seen_links = set()
    all_results = []

    # detection flags
    platform_hits = {k: False for k in PLATFORMS.keys()}

    print("\n[+] Starting username OSINT search...\n")

    with DDGS() as ddgs:
        for query in queries:
            print(f"[+] Searching: {query}")

            try:
                results = ddgs.text(query, max_results=20)
            except Exception:
                print(f"[!] Query error: {query}")
                continue

            for r in results:
                link = r.get("href")
                title = r.get("title")

                if not link or not title:
                    continue

                if link in seen_links:
                    continue

                if "duckduckgo.com" in link:
                    continue

                if not is_relevant_result(link, title):
                    continue

                detected = detect_platform(link, title)

                # skip useless results (no platform detected)
                if not detected:
                    continue

                seen_links.add(link)

                for d in detected:
                    platform_hits[d] = True

                print(f"[+] {title}")
                print(link, "\n")

                all_results.append({
                    "query": query,
                    "title": title,
                    "link": link,
                    "categories": list(detected)
                })

    print("\n[+] Summary:\n")

    for p, v in platform_hits.items():
        status = "✔" if v else "✘"
        print(f"{p}: {status}")

    output = {
        "username": username,
        "platforms_detected": platform_hits,
        "results": all_results
    }

    with open(f"username_{username}.json", "w") as f:
        json.dump(output, f, indent=4)

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="Username to search")

    args = parser.parse_args()

    if args.username:
        search_username(args.username)
    else:
        print("[-] Provide a username with --username")
