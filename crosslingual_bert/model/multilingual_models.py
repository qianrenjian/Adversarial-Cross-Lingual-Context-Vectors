import copy
from itertools import chain
import torch
import torch.nn as nn
import torch.nn.functional as F

from .bert_official import BertConfig, BertModel
from .translator import TranslatorModel


class MultilingualBert(nn.Module):
	"""Cross-lingual context vector model using transformer architecture
	"""
	def __init__(self, languages, config: BertConfig):
		super().__init__()
		self.shared = BertModel(config)
		self.private = {language: BertModel(config) for language in languages}
	
	def forward(self, language, input_ids, token_type_ids=None, attention_mask=None):
		assert language in self.private
		shared_vectors, shared_pooled = self.shared(input_ids, token_type_ids, attention_mask)
		private_vectors, private_pooled = self.private[language](input_ids, token_type_ids, attention_mask)
		hidden_vectors = [torch.cat((sv, pv), -1) for sv, pv in zip(shared_vectors, private_vectors)]
		pooled_output = torch.cat((shared_pooled, private_pooled), -1)
		return hidden_vectors, pooled_output

	def language_parameters(self, language):
		assert language in self.private
		return chain(self.shared.parameters(), self.private[language].parameters())


class MultilingualTranslator(nn.Module):
	"""Universal to target language translation model using transformer architecture
	"""
	def __init__(self, model: MultilingualBert, target_language: str, config: BertConfig):
		assert target_language in model.private
		super().__init__()
		self.multilingual_model = model
		
		# double intermediate and hidden size to account for shared-private model
		config = copy.copy(config)
		config.intermediate_size *= 2
		config.hidden_size *= 2

		self.translator_model = TranslatorModel(config)
		self.target_language = target_language

	def forward(self, language, input_ids, target_ids, input_mask=None, target_mask=None):
		language_vectors, _ = self.multilingual_model(language, input_ids, attention_mask=input_mask)
		target_vectors, _ = self.multilingual_model(self.target_language, target_ids, attention_mask=target_mask)
		return self.translator_model(language_vectors[-1], target_vectors[-1], input_mask, target_mask)
