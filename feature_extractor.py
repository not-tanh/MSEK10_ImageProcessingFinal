from icecream import ic
import torch
import torch.nn as nn
from transformers import ViTImageProcessor, ViTForImageClassification


class FeatureDescriptor:
    def __init__(self):
        ic('Loading model')
        hf_model_name = 'google/vit-base-patch16-224'
        self.feature_extractor = ViTImageProcessor.from_pretrained(hf_model_name)
        self.model = ViTForImageClassification.from_pretrained(hf_model_name)
        self.model.classifier = nn.Identity()
        self.model.eval()
        ic('Finished loading model')

    def __call__(self, images, **kwargs):
        with torch.no_grad():
            inputs = self.feature_extractor(images=images, return_tensors="pt")
            outputs = self.model(**inputs).logits.numpy()
            return outputs
