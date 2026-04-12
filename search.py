from ddgs import DDGS
import json
import argparse


# relevant domains
VALID_DOMAINS = [
    "loquosex.com",
    "destacamos.com",
    "publicontactos.com",
    "choosescorts.com",
    "nuevapasion.com",
    "slumi.com"
]

# keywords to filter useful results
KEYWORDS = [
    "escort",
    "puta",
    "masajes",
    "contactos",
    "vip",
    "independiente"
]


def is_valid_result(link):
    return any(domain in link for domain in VALID_DOMAINS)


def is_relevant(title):
    return any(word in title.lower() for word in KEYWORDS)


# skip generic pages
def is_specific_ad(link):
    return any(x in link for x in [
        "details",
        ".html"
    ])


def search_phone(phone):
    queries = [
        f'"{phone}"',
        f'"{phone}" escort',
        f'"{phone}" site:loquosex.com',
        f'"{phone}" site:destacamos.com',
        f'"{phone}" site:publicontactos.com',
        f'"{phone}" site:choosescorts.com'
    ]

    all_results = []
    seen_links = set()

    print("\n[+] Starting OSINT search...\n")

    with DDGS() as ddgs:
        for query in queries:
            print(f"[+] Searching: {query}")

            try:
                results = ddgs.text(query, max_results=15)
            except Exception as e:
                if "No results found" in str(e):
                    print(f"[!] No results for query: {query}")
                else:
                    print(f"[!] Unexpected error in query '{query}': {e}")
                continue

            for r in results:
                link = r.get("href")
                title = r.get("title")

                if not link or not title:
                    continue

                # skip duplicates
                if link in seen_links:
                    continue

                # avoid junk links
                if "duckduckgo.com" in link:
                    continue

                # filter by content
                if not is_valid_result(link):
                    continue

                # filter by content
                if not is_relevant(title):
                    continue

                # skip categories/lists
                if not is_specific_ad(link):
                    continue

                seen_links.add(link)

                domain = link.split("/")[2]

                print(f"[+] {title}")
                print(link, "\n")

                all_results.append({
                    "query": query,
                    "title": title,
                    "link": link,
                    "domain": domain
                })

    print(f"\n[+] Total results collected: {len(all_results)}")

    # save results
    with open(f"results_{phone}.json", "w") as f:
        json.dump(all_results, f, indent=4)

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", help="Phone number to search")

    args = parser.parse_args()

    if args.phone:
        search_phone(args.phone)
    else:
        print("[-] Introduce a phone number with --phone")
