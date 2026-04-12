from ddgs import DDGS
import json
import argparse
import re


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


# generate phone variants 
def generate_phone_variants(phone):
    phone = phone.replace(" ", "")

    variants = [
        phone,
        f"+34{phone}",
        f"0034{phone}",
        f"{phone[:3]} {phone[3:5]} {phone[5:7]} {phone[7:]}"
    ]

    return list(set(variants))


# extract name
def extract_name(title):
    words = title.split()
    if len(words) > 0:
        return words[0]
    return None


# a quick scorecard to prioritize results
def score_result(title, link):
    score = 0

    if any(word in title.lower() for word in KEYWORDS):
        score += 2

    if any(domain in link for domain in VALID_DOMAINS):
        score += 2

    if "details" in link:
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

                # filter by domain
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
                name = extract_name(title)
                score = score_result(title, link)

                print(f"[+] {title}")
                print(link, "\n")

                all_results.append({
                    "query": query,
                    "title": title,
                    "link": link,
                    "domain": domain,
                    "name": name,
                    "score": score
                })

    print(f"\n[+] Total results collected: {len(all_results)}")

    # sort by score (highest first)
    all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)

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
