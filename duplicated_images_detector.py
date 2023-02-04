import os
import time

import cv2
import imutils
import numpy as np
import scipy.fftpack


def dhash(image, hash_size=8):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum(2 ** i for i, v in enumerate(diff.flatten()) if v)


def phash(image, hash_size=8, highfreq_factor=4):
    img_size = hash_size * highfreq_factor
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pixels = cv2.resize(gray, (img_size, img_size))
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    return diff


if __name__ == '__main__':
    t = time.time()
    hash_dict = dict()
    for img in os.scandir('images'):
        if img.name.startswith('.'):
            continue
        image_hash = dhash(cv2.imread(img.path))
        if image_hash not in hash_dict:
            hash_dict[image_hash] = []
        hash_dict[image_hash].append(img.path)
    print('Execution time:', time.time() - t)
    for image_hash in hash_dict:
        if len(hash_dict[image_hash]) > 1:
            print('Found %s duplicated images' % len(hash_dict[image_hash]))
            montage = imutils.build_montages(
                [cv2.imread(path) for path in hash_dict[image_hash]], (64, 64),
                (len(hash_dict[image_hash]), 1)
            )
            cv2.imshow(str(image_hash), montage[0])
            while True:
                if cv2.waitKey(1) == ord('q'):
                    break
            cv2.destroyAllWindows()
