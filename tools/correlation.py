import json
import argparse
import glob
import os


def load_json_files(path):
    files = glob.glob(path)
    data = []

    for f in files:
        try:
            with open(f, "r") as file:
                content = json.load(file)

                if "results" in content:
                    data.append({
                        "file": os.path.basename(f),
                        "data": content
                    })
        except:
            continue

    return data


def extract_links(results):
    links = set()

    for r in results:
        link = r.get("link")
        if link:
            links.add(link)

    return links


def extract_domains(links):
    domains = set()

    for link in links:
        try:
            domain = link.split("/")[2]
            domains.add(domain)
        except:
            continue

    return domains


def correlate(data):
    correlations = []

    for i in range(len(data)):
        for j in range(i + 1, len(data)):

            file1 = data[i]
            file2 = data[j]

            links1 = extract_links(file1["data"]["results"])
            links2 = extract_links(file2["data"]["results"])

            domains1 = extract_domains(links1)
            domains2 = extract_domains(links2)

            common_links = links1.intersection(links2)
            common_domains = domains1.intersection(domains2)

            if common_links or common_domains:
                correlations.append({
                    "file_1": file1["file"],
                    "file_2": file2["file"],
                    "common_links": list(common_links),
                    "common_domains": list(common_domains)
                })

    return correlations


def main(path):
    data = load_json_files(path)

    if not data:
        print("[-] No valid JSON files found")
        return

    correlations = correlate(data)

    if not correlations:
        print("[-] No correlations found")
        return

    print("\n[+] Correlations found:\n")

    for c in correlations:
        print(f"{c['file_1']}  <-->  {c['file_2']}")

        if c["common_links"]:
            print("  [links]")
            for l in c["common_links"]:
                print(f"   - {l}")

        if c["common_domains"]:
            print("  [domains]")
            for d in c["common_domains"]:
                print(f"   - {d}")

        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to JSON files (e.g. data/*.json)")

    args = parser.parse_args()

    if args.path:
        main(args.path)
    else:
        print("[-] Provide a path like data/*.json")
