import json
from transformers.utils.hub import cached_file

# Get vocab.json path
vocab_file_path = cached_file(path_or_repo_id="gpt2", filename="vocab.json")

# Load vocab.json into a Python dictionary
with open(vocab_file_path, "r", encoding="utf-8") as f:
    vocab = json.load(f)

# Now this will work:
print("Total tokens in vocab:", len(vocab))
