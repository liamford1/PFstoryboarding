import json

input_file = "restructured_for_finetuning.jsonl"     # replace with your actual file path
output_file = "output.jsonl"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        item = json.loads(line)
        if "output" in item:
            item["response"] = item.pop("output")
        json.dump(item, outfile)
        outfile.write("\n")
