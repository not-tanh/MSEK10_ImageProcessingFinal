import json

from annoy import AnnoyIndex
from icecream import ic

from pipeline import Pipeline
from preprocessor import Preprocessor
from feature_extractor import FeatureDescriptor
from config import FEATURE_DIM, INDEX_PATH


class SearchEngine:
    def __init__(self):
        ic('Reading index')
        self.index = AnnoyIndex(FEATURE_DIM, 'euclidean')
        self.index.load(INDEX_PATH)

        ic('Reading metadata')
        with open('new_data.json', 'r') as f:
            self.data = json.load(f)

        ic('Database size:', len(self.data))
        self.pipeline = Pipeline([Preprocessor(), FeatureDescriptor()])

    def __call__(self, image, k=10, **kwargs):
        feature = self.pipeline([image])
        ic(feature.shape)
        indexes, distances = self.index.get_nns_by_vector(feature[0], k, include_distances=True)
        # distances, indexes = distances.squeeze(), indexes.squeeze()
        print('Distances:', distances)
        print('Indexes:', indexes)
        results = [self.data[i] for i in indexes if i < len(self.data)]
        return results
