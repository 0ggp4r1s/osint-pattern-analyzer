import requests
from bs4 import BeautifulSoup
from rich import print
import argparse
import json


def duckduckgo_search(query):
    url = "https://html.duckduckgo.com/html/"

    data = {
        "q": query
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(url, data=data, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for a in soup.find_all("a"):
        href = a.get("href")
        text = a.get_text(strip=True)

        if href and text and "http" in href:
            results.append({
                "title": text,
                "link": href
            })

    return results


def run(phone):
    queries = [
	f'"{phone}"',
	f'"{phone}" escort',
        f'"{phone}" site:loquosex.com',
        f'"{phone}" site:escort',
        f'"{phone}" site:destacamos.com',
        f'"{phone}" site:oasisdemadrid.com',
        f'"{phone}" "independiente"',
        f'"{phone}" site:nuevapasion.com',
        f'"{phone}" site:spalumi.com',
        f'"{phone}" site:choosescorts.com',
        f'"{phone}" site:publicontactos.com',

]

    all_results = []

    for q in queries:
        print(f"\n[bold cyan]Searching:[/bold cyan] {q}")

        results = duckduckgo_search(q)

        for r in results:
            print(f"[green]{r['title']}[/green]")
            print(f"[blue]{r['link']}[/blue]\n")

            all_results.append({
                "query": q,
                "title": r["title"],
                "link": r["link"]
            })

    # Save results
    with open(f"results_{phone}.json", "w") as f:
        json.dump(all_results, f, indent=4)

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", help="Phone number to search")

    args = parser.parse_args()

    if args.phone:
        run(args.phone)
    else:
        print("[red]Introduce a phone number with --phone[/red]")
