import paddle.nn as nn
import paddle
import numpy as np
import paddle.nn.functional as F
import json
from ppcls.utils import logger
import sys



class CELossWordTree(nn.Layer):
    r"""
    to compute the each classic loss
    """

    def __init__(self, wordtree_json_path):
        super(CELossWordTree, self).__init__()

        self.wordtree_json_path = wordtree_json_path
        self._generate_wordtree()

    def _generate_wordtree(self):
        try:
            with open(self.wordtree_json_path, 'r') as f:
                self.word_tree = json.load(f)
        except FileNotFoundError:
            logger.error(f"the word tree json file:{self.wordtree_json_path} is not exist, please check")
            sys.exit(-1)

    def forward(self, x, label):
        """
        directly compute the total output CEloss currently.
        """
        if isinstance(x, dict):
            x = x["logits"]
        word_tree_loss = F.cross_entropy(x, label, soft_label=True)

        return {"Word_Tree_loss":word_tree_loss}

