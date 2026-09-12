import gzip
import json

import requests

compressed_sizes = []
uncompressed_sizes = []
number_of_events = []
type_2_count = {}

#all the top level keys we see
top_level_key_union = set()

#top level keys that are common to every record
top_level_key_intersection = set()

type_2_payload_keys = {}

for day in range(1,2):
    for hour in range(1):
        print(f"Processing day {day}, hour {hour}")

        URL = f"https://data.gharchive.org/2026-01-{day:02d}-{hour}.json.gz"

        # response = requests.get(URL)

        # # Get the compressed size of the response in MB
        # compressed_size_mb = len(response.content) / (1024 ** 2)
        # print(f"Compressed size: {compressed_size_mb:.6f} MB")
        # compressed_sizes.append(compressed_size_mb)

        # # Get the uncompressed size of the response in MB
        # uncompressed_size_mb = len(gzip.decompress(response.content)) / (1024 ** 2)
        # print(f"Uncompressed size: {uncompressed_size_mb:.6f} MB")
        # uncompressed_sizes.append(uncompressed_size_mb)

        # stream=True + r.raw lets gzip decompress incrementally, so the ~38 MB
        # compressed file never has to be fully expanded in memory.
        with requests.get(URL, stream=True) as response:
            response.raise_for_status()
            with gzip.open(response.raw, mode="rt", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    event = json.loads(line)

                    top_level_keys = set(event.keys())

                    for key in top_level_keys:
                        if event[key] is None:
                            top_level_keys.remove(key)


                    top_level_key_union.update(top_level_keys)
                    if not top_level_key_intersection:
                        top_level_key_intersection = top_level_keys
                    else:
                        top_level_key_intersection.intersection_update(top_level_keys)

                    event_type = event.get("type")
                    if event_type not in type_2_count:
                        # Print the event if its type has not been seen before
                        print(json.dumps(event, indent=2, ensure_ascii=False))
                        print("################################################################################")

                    if event_type:
                        type_2_count[event_type] = type_2_count.get(event_type, 0) + 1

                        type_2_payload_keys[event_type] = type_2_payload_keys.get(event_type, set())
                        if "payload" in event:
                            type_2_payload_keys[event_type].update(event["payload"].keys())
                    

        num_events = i+1
        number_of_events.append(num_events)

print("Top level key union:")
print(top_level_key_union)
print("Top level key intersection:")
print(top_level_key_intersection)
print("Type to payload keys mapping:")
for event_type, payload_keys in type_2_payload_keys.items():
    print(f"{event_type}: {payload_keys}")


# avg_compressed_size = sum(compressed_sizes) / len(compressed_sizes)
# avg_uncompressed_size = sum(uncompressed_sizes) / len(uncompressed_sizes)
# avg_number_of_events = sum(number_of_events) / len(number_of_events)

# print(f"Average compressed size: {avg_compressed_size:.6f} MB")
# print(f"Average uncompressed size: {avg_uncompressed_size:.6f} MB")
# print(f"Average number of events: {avg_number_of_events:.2f}")

# URL = f"https://data.gharchive.org/2026-01-01-15.json.gz"
# with requests.get(URL, stream=True) as response:
#     response.raise_for_status()
#     with gzip.open(response.raw, mode="rt", encoding="utf-8") as f:
#         for i, line in enumerate(f):
#             event = json.loads(line)
#             print(json.dumps(event, indent=2, ensure_ascii=False))
#             if i > 3:
#                 break

# URL = f"https://data.gharchive.org/2026-01-01-15.json.gz"


# interesting_event_types = ["PullRequestEvent",
#                            "PullRequestReviewEvent",
#                            "PullRequestReviewCommentEvent",
#                            "IssueCommentEvent"]

# with requests.get(URL, stream=True) as response:
#     response.raise_for_status()
#     with gzip.open(response.raw, mode="rt", encoding="utf-8") as f:
#         for i, line in enumerate(f):
#             event = json.loads(line)
#             event_type = event.get("type")
#             if event_type not in type_2_count:
#                 # Print the event if its type has not been seen before
#                 if event_type in interesting_event_types:
#                     print(json.dumps(event, indent=2, ensure_ascii=False))
#                     print("################################################################################")

#             if event_type:
#                 type_2_count[event_type] = type_2_count.get(event_type, 0) + 1

# print(type_2_count)