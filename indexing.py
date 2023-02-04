import os

# import faiss
import numpy as np
import h5py
from annoy import AnnoyIndex


def load_indexes_from_h5(h5_path):
    indexes = []
    cnt = 0
    while True:
        filepath = os.path.join(h5_path, 'data-%s.h5' % cnt)
        if os.path.exists(filepath):
            hf = h5py.File(filepath, 'r')
            batch = np.array(hf.get('data'))
            hf.close()
            indexes.append(batch)
            cnt += 1
        else:
            break
    indexes = np.vstack(indexes)
    return indexes.astype('float32')


# def build_index(matrix: np.ndarray):
#     n, dimension = matrix.shape
#     index = faiss.index_factory(dimension, "IDMap,Flat")
#     ids = np.array([i for i in range(len(matrix))])
#     index.add_with_ids(matrix, ids)
#     print('Total length:', index.ntotal)
#     faiss.write_index(index, 'faiss_index')


def build_index(matrix: np.ndarray):
    size, dim = matrix.shape
    index = AnnoyIndex(dim, 'euclidean')
    for i in range(size):
        index.add_item(i, matrix[i])
    index.build(1000)
    index.save('AnnoyIndex-eulidean.ann')


if __name__ == '__main__':
    # build_index(load_indexes_from_h5('h5_indexes'))
    m = load_indexes_from_h5('h5_indexes')
    print(m.shape)
