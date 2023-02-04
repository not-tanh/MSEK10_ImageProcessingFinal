import os
import json

import h5py
import numpy as np

from preprocessor import Preprocessor
from feature_extractor import FeatureDescriptor
from pipeline import Pipeline


def extract_ViT_features():
    pipeline = Pipeline([Preprocessor(), FeatureDescriptor()])
    with open('data.json', 'r') as f:
        data = json.load(f)
    features = []
    print('Extracting features...')
    new_data = []
    batch = []
    batch_count = 0
    save_count = 0
    for image_info in data:
        image_path = image_info.get('image_path', None)
        if image_path is None or not os.path.exists(image_path):
            continue
        batch.append(image_path)
        new_data.append(image_info)

        if len(batch) == 128:
            feature = pipeline(batch)
            features.append(feature)
            batch = []
            batch_count += 1
            print('Batch count', batch_count)
            if len(features) == 10:
                hf = h5py.File('h5_indexes/data-%s.h5' % save_count, 'w')
                hf.create_dataset('data', data=np.vstack(features))
                hf.close()
                print('Saved data-%s.h5' % save_count)
                features = []
                save_count += 1
    # last batch
    if batch:
        feature = pipeline(batch)
        features.append(feature)
        hf = h5py.File('h5_indexes/data-%s.h5' % save_count, 'w')
        hf.create_dataset('data', data=np.vstack(features))
        hf.close()
        print('Saved data-%s.h5' % save_count)
    print('Features extracted')
    with open('new_data.json', 'w') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    extract_ViT_features()
