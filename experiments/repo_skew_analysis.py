import requests
import gzip
import json

repo_id_2_count = {}

for day in range(1, 30):
    for hour in range(24):
        print(f"Processing day {day}, hour {hour}")

        URL = f"https://data.gharchive.org/2026-01-{day:02d}-{hour}.json.gz"


        with requests.get(URL, stream=True) as response:
            response.raise_for_status()
            with gzip.open(response.raw, mode="rt", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    event = json.loads(line)

                    repo = event.get("repo")

                    if repo:
                        repo_id = repo.get("id")

                    if repo_id:
                        repo_id_2_count[repo_id] = repo_id_2_count.get(repo_id, 0) + 1


# Sort by count in descending order and print only the top 10
sorted_repo_id_2_count = sorted(repo_id_2_count.items(), key=lambda x: x[1], reverse=True)

total_count = sum(repo_id_2_count.values())

for repo_id, count in sorted_repo_id_2_count[:25]:
    print(f"Repo ID: {repo_id}, Count: {count}, Fraction: {count/total_count:.4f}")



# get the top 1 percent of repositories by count
top_1_percent_index = max(1, len(sorted_repo_id_2_count) // 100)
top_1_percent_repos = sorted_repo_id_2_count[:top_1_percent_index]

top_1_percent_total_count = sum(count for _, count in top_1_percent_repos)
print(f"Top 1% total count: {top_1_percent_total_count}, Fraction: {top_1_percent_total_count/total_count:.4f}")