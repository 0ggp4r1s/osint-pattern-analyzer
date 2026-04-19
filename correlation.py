import json
import glob
import argparse
from collections import defaultdict
from urllib.parse import urlparse

def load_json_files(path):
    files = glob.glob(path)
    data = []

    for f in files:
        try:
            with open(f, "r") as file:
                data.append(json.load(file))
        except:
            continue

    return data


def correlate(url):
    try:
        return urlparse(url).netloc
    except:
        return ""

def correlate(data):
    all_links = defaultdict(list)
    platform_summary = defaultdict(int)

    for dataset in data:
        source = list(dataset.keys())[0]

        for result in dataset.get("results", []):
            link = result.get("link")
            categories = result.get("categories",[])

            if not link:
                continue

            domain = extract_domain(link)

            all_links[domain].append({
                "link": link,
                "source": source,
                "categories": categories
            })

            for c in categories:
                platform_summary[c] +=1

    # detect overlaps
    overlaps = {}



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(--path, help="Path to JSON files (e.g data/*.json)")

    args = parser.parse_args()

    if not args.path:
        print("[-] Provide path to JSON files")
        return

    data = load_json_files(args.path)

    if not data:
        print("[-] NO valid JSON files found")
        return

    result = correlation(data)

    print_summary(result)

    with open("correlation_output.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    main()
