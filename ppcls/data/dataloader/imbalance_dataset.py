#   Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function


import numpy as np
import random
import os
from ppcls.data.preprocess import transform
from .common_dataset import CommonDataset
from ppcls.utils import logger

class ImBalanceImageNetDataset(CommonDataset):
    def __init__(
            self,
            image_root,
            cls_label_path,
            transform_ops=None,
            delimiter=None):
        self.delimiter = delimiter if delimiter is not None else "\t"
        super(ImBalanceImageNetDataset, self).__init__(image_root, cls_label_path, transform_ops)

    def _load_anno(self, seed=None):
        assert os.path.exists(self._cls_path)
        assert os.path.exists(self._img_root)
        self.images = []
        self.labels = []
        self.class_list = {}

        with open(self._cls_path) as fd:
            lines = fd.readlines()
            if seed is not None:
                np.random.RandomState(seed).shuffle(lines)
            for index, l in enumerate(lines):
                l = l.strip().split(self.delimiter)
                self.images.append(os.path.join(self._img_root, l[0]))
                label = np.int64(l[1])
                self.labels.append(label)
                if not label in self.class_list:
                    self.class_list[label] = []
                self.class_list[label].append(index)
                assert os.path.exists(self.images[-1])
        self.num_class_list = [len(class_num) for _, class_num in self.class_list.items()]
        # print("num_class_list:", self.num_class_list)
        # print("class_list:", self.class_list)

        
    def __getitem__(self, idx):
        """
        class balance sampler,
        override the father class common_dataset.__getitem__ functions
        """
        ## class balance sampler
        sample_class = random.randint(0, len(self.class_list.keys()) - 1)
        sampler_index = self.class_list[sample_class]
        idx = np.random.choice(sampler_index)

        try:
            with open(self.images[idx], 'rb') as f:
                img = f.read()
            if self._transform_ops:
                img = transform(img, self._transform_ops)
            img = img.transpose((2, 0, 1))
            return (img, self.labels[idx])

        except Exception as ex:
            logger.error("Exception occured when parse line: {} with msg: {}".
                         format(self.images[idx], ex))
            rnd_idx = np.random.randint(self.__len__())
            return self.__getitem__(rnd_idx)