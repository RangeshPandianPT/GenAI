from transformers import GPT2TokenizerFast
from transformers.utils.hub import cached_file

# Load the tokenizer
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

# Get vocab file path using Hugging Face utility
vocab_file_path = cached_file(path_or_repo_id="gpt2", filename="vocab.json")

print("Vocab file path:", vocab_file_path)
