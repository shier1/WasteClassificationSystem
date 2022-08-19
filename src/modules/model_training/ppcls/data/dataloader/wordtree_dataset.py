from __future__ import print_function

import numpy as np
import os

from .common_dataset import CommonDataset


class WordTreeDataset(CommonDataset):
    def __init__(
            self,
            image_root,
            cls_label_path,
            class_nums,
            transform_ops=None,
            delimiter=None):
        self.delimiter = delimiter if delimiter is not None else "\t"
        self.class_nums = class_nums
        super(WordTreeDataset, self).__init__(image_root, cls_label_path, transform_ops)

    def _load_anno(self, seed=None):
        assert os.path.exists(self._cls_path)
        assert os.path.exists(self._img_root)
        self.images = []
        self.labels = []

        with open(self._cls_path) as fd:
            lines = fd.readlines()
            if seed is not None:
                np.random.RandomState(seed).shuffle(lines)
            for l in lines:
                l = l.strip().split(self.delimiter)
                self.images.append(os.path.join(self._img_root, l[0]))
                label = np.zeros(shape=self.class_nums, dtype=np.float32)

                self.label_wordtree = np.int64(l[1])
                self.label_class = np.int64(l[2])
                label[self.label_wordtree] = 1
                label[self.label_class] = 1
                self.labels.append(label)
                assert os.path.exists(self.images[-1])
