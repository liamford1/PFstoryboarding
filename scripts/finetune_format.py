import json

with open("../data/penn/final_training_dataset.jsonl", "r") as infile, open("sft_data.jsonl", "w") as outfile:
    for line in infile:
        ex = json.loads(line)
        json.dump({"instruction": ex["prompt"], "output": ex["completion"]}, outfile)
        outfile.write("\n")
