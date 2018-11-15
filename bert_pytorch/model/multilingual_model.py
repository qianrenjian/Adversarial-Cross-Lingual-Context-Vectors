import torch
import torch.nn as nn


class PublicPrivateModel(nn.Module):
	def __init__(self, public, private):
		self.public = public
		self.private = private
	
	def forward(self, input_ids):
		return torch.cat([self.public(input_ids), self.private(input_ids)], -1)


class MultilingualModel:
	def __init__(self, language_ids, arch, *arch_args, **arch_kwargs):
		self.ltoi = language_ids # language to index/label id
		self.public_model = arch(*arch_args, **arch_kwargs)
		self.private_models = [arch(*arch_args, **arch_kwargs) for _ in range(len(language_ids))]
		self.language_models = [PublicPrivateModel(self.public_model, private_model) for private_model in self.private_models]
	
	def __getitem__(self, index):
		if type(index) is str:
			return self.language_models[self.ltoi[index]]
		else:
			return self.language_models[index]
	
	def __len__(self):
		return len(self.ltoi)


class PretrainingWrapper(nn.Module):
	def __init__(self, model, adversary, hidden, vocab_size): 
		self.model = model
		self.adversary = adversary

		# variables necessary for prediction tasks
		self.token_linear = nn.Linear(hidden, vocab_size)
		self.next_linear = nn.Linear(hidden, 2)
	
	def __forward__(self, input_ids):
		context_vectors = self.model(input_ids)
		
		# logits for prediction tasks
		token_logits = self.token_linear(context_vectors)
		next_logits = self.next_linear(context_vectors)
		language_logits = self.adversary(context_vectors)

		# public-private vector similarity loss
		dim = context_vectors.size(-1) // 2
		public_vectors, private_vectors = torch.split(context_vectors, dim, -1)

		diff_loss = torch.bmm(private_vectors, torch.transpose(public_vectors, 2, 1))
		diff_loss = torch.sum(diff_loss ** 2) / context_vectors.size(0)
		return token_logits, next_logits, language_logits, diff_loss


class PretrainingModel:
	def __init__(self, mutlilingual_model, adversary, vocab_size):
		self.mutlilingual_model = multilingual_model
		# add necessary prediction task
		self.pretraining_models = [PretrainingWrapper(model, adversary, vocab_size) for model in self.multilingual_model]
		
	def __getitem__(self, index):
		if type(index) is str:
			return self.pretraining_models[self.multilingual_model.ltoi(index)]
		else:
			return self.pretraining_models[index]
	
	def __len__(self):
		return len(self.multilingual_model)


