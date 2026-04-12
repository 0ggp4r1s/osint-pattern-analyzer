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
    """Check if link belongs to known relevant domains"""
    return any(domain in link for domain in VALID_DOMAINS)


def is_ad_link(link):
    """Try to detect if link is a real ad and not a generic listing"""
    link = link.lower()

    # clear indicators of real ad pages
    if any(x in link for x in ["details", ".html", "contactos"]):
        return True

    # avoid generic/category pages
    if any(x in link for x in [
        "categoria",
        "tag",
        "listado",
        "anuncios-escort"
    ]):
        return False

    # fallback
    return True


def detect_type(title):
    """Detect if the ad is individual, group or duo"""
    t = title.lower()

    if any(word in t for word in GROUP_KEYWORDS):
        return "group"

    if any(word in t for word in DUO_KEYWORDS):
        return "duo"

    return "individual"


def generate_phone_variants(phone):
    """Generate different formats of the phone number"""
    phone = phone.replace(" ", "")

    return list(set([
        phone,
        f"+34{phone}",
        f"0034{phone}",
        f"{phone[:3]} {phone[3:5]} {phone[5:7]} {phone[7:]}"
    ]))


def contains_phone(title, link, variants):
    """Ensure the result actually contains the phone number"""
    text = f"{title} {link}".replace(" ", "")

    for v in variants:
        if v.replace(" ", "") in text:
            return True

    return False


def score_result(title, link):
    """Score results to prioritize better matches (not filtering)"""
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

    # domain-specific queries
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

                # avoid duplicates
                if link in seen_links:
                    continue

                # skip DDG internal links
                if "duckduckgo.com" in link:
                    continue

                # domain filter
                if not is_valid_domain(link):
                    continue

                # avoid generic pages
                if not is_ad_link(link):
                    continue

                # ensure phone is really present
                if not contains_phone(title, link, variants):
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

    # sort by score (higher first)
    all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)

    # save results
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
