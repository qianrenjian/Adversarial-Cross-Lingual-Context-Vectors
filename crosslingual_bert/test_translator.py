import torch

from model import TranslatorModel, BertConfig
import pdb

print("Starting unittests for translator model...")

vocab_size = 10000
seq_len = 4
batch_size = 5

config = BertConfig(vocab_size=vocab_size)
model = TranslatorModel(config)
print("passed initialization test")

test_encoder = torch.rand(batch_size, seq_len, config.hidden_size)
test_ids = torch.randint(high=vocab_size, size=(batch_size, seq_len), dtype=torch.long)
"""test_layers, test_pool = model(test_encoder, test_ids)

assert len(test_layers) == config.num_hidden_layers
for layer in test_layers:
	assert layer.shape == (batch_size, seq_len, config.hidden_size)

assert test_pool.shape == (batch_size, config.hidden_size)"""

print("passed forward propagation tests")

encoder_mask = torch.randint(high=2, size=(batch_size, seq_len), dtype=torch.long)
id_mask = torch.randint(high=2, size=(batch_size, seq_len), dtype=torch.long)

test_layers, test_pool = model(test_encoder, test_ids, encoder_mask, id_mask)

assert len(test_layers) == config.num_hidden_layers
for layer in test_layers:
	assert layer.shape == (batch_size, seq_len, config.hidden_size)

assert test_pool.shape == (batch_size, config.hidden_size)

print("passed masking tests")

print("passed all tests")