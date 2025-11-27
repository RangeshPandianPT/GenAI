from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

# 1. Initialize empty BPE tokenizer
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# 2. Set a pre-tokenizer (splits text on whitespace)
tokenizer.pre_tokenizer = Whitespace()

# 3. Trainer settings
trainer = BpeTrainer(
    vocab_size=1000,  # You can set 5000, 10000, 50000, etc.
    special_tokens=[
        "[UNK]",
        "[PAD]",
        "[CLS]",
        "[SEP]",
        "[MASK]"
    ]
)

# 4. Your dataset
files = ["words.txt"]   # Put large text data inside words.txt

# 5. Train the tokenizer
tokenizer.train(files, trainer)

# 6. Save the tokenizer model (produces two files)
tokenizer.model.save(".", "my_bpe")
