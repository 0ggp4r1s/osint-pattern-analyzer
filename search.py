from ddgs import DDGS
import json
import argparse


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
                results = ddgs.text(query, max_results=10)
            except Exception as e:
                print(f"[!] Error: {e}")
                continue

            for r in results:
                link = r.get("href")
                title = r.get("title")

                if not link or not title:
                    continue

                # delete duplicates
                if link in seen_links:
                    continue

                seen_links.add(link)

                # prevent waste
                if "duckduckgo.com" in link:
                    continue

                print(f"[+] {title}")
                print(link, "\n")

                all_results.append({
                    "query": query,
                    "title": title,
                    "link": link
                })

    print(f"\n[+] Total results collected: {len(all_results)}")

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
