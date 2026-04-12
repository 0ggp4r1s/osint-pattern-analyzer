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

# useful keywords
KEYWORDS = [
    "escort",
    "puta",
    "masajes",
    "contactos",
    "vip",
    "independiente"
]

# group / duo detection
GROUP_KEYWORDS = ["amigas", "chicas", "grupo", "varias"]
DUO_KEYWORDS = ["duo", "dos", "pareja"]


def is_valid_domain(link):
    return any(domain in link for domain in VALID_DOMAINS)


def is_ad_link(link):
    link = link.lower()

    # typical signs of a genuine ad
    signals = [
        "escort",
        "contactos",
        "anuncio",
        "details",
        "telefono",
        ".html"
    ]

    return any(s in link for s in signals)


def detect_type(title):
    t = title.lower()

    if any(word in t for word in GROUP_KEYWORDS):
        return "group"

    if any(word in t for word in DUO_KEYWORDS):
        return "duo"

    return "individual"


# generate variations of the number
def generate_phone_variants(phone):
    phone = phone.replace(" ", "")

    return list(set([
        phone,
        f"+34{phone}",
        f"0034{phone}",
        f"{phone[:3]} {phone[3:5]} {phone[5:7]} {phone[7:]}"
    ]))


# fine scoring 
def score_result(title, link):
    score = 0
    title_lower = title.lower()

    if any(word in title_lower for word in KEYWORDS):
        score += 2

    if "details" in link:
        score += 2

    if "contactos" in link:
        score += 1

    return score


def search_phone(phone):

    variants = generate_phone_variants(phone)

    queries = []
    for v in variants:
        queries.append(f'"{v}"')
        queries.append(f'"{v}" escort')

    queries += [
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
                results = ddgs.text(query, max_results=20)
            except Exception as e:
                if "No results found" in str(e):
                    print(f"[!] No results for query: {query}")
                else:
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

                if not is_valid_domain(link):
                    continue

                if not is_ad_link(link):
                    continue

                seen_links.add(link)

                domain = link.split("/")[2]
                ad_type = detect_type(title)
                score = score_result(title, link)

                print(f"[+] {title}")
                print(link, "\n")

                all_results.append({
                    "query": query,
                    "title": title,
                    "link": link,
                    "domain": domain,
                    "type": ad_type,
                    "score": score
                })

    print(f"\n[+] Total results collected: {len(all_results)}")

    # sort without deleting anything
    all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)

    with open(f"results_{phone}.json", "w") as f:
        json.dump(all_results, f, indent=4)

    # summary 
    print("\n[+] Summary:\n")

    types = set(r["type"] for r in all_results)

    print(f"[+] Ad types detected: {list(types)}")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", help="Phone number to search")

    args = parser.parse_args()

    if args.phone:
        search_phone(args.phone)
    else:
        print("[-] Introduce a phone number with --phone")
