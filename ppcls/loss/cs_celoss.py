import paddle.nn as nn
import paddle
import numpy as np
import paddle.nn.functional as F


class CostSensitiveCE(nn.Layer):
    r"""
        Equation: Loss(z, c) = - (\frac{N_min}{N_c})^\gamma * CrossEntropy(z, c),
        where gamma is a hyper-parameter to control the weights,
            N_min is the number of images in the smallest class,
            and N_c is the number of images in the class c.
    The representative re-weighting methods, which assigns class-dependent weights to the loss function
    Args:
        gamma (float or double): to control the loss weights: (N_min/N_i)^gamma
    """

    def __init__(self, num_class_list, gamma):
        super(CostSensitiveCE, self).__init__()
        self.num_class_list = num_class_list
        self.csce_weight = paddle.to_tensor(np.array([(min(self.num_class_list) / N)**gamma for N in self.num_class_list], dtype=np.float32))

    def forward(self, x, label):
        if isinstance(x, dict):
            x = x["logits"]

        if label.shape[-1] == x.shape[-1]:
            label = F.softmax(label, axis=-1)
            soft_label = True
        else:
            soft_label = False
        cs_ce_loss = F.cross_entropy(x, label=label, soft_label=soft_label, weight=self.csce_weight)
        cs_ce_loss = cs_ce_loss.mean()
        return {"CS_CELoss":cs_ce_loss}

# if __name__ == "__main__":
#     criterion = CostSensitiveCE(num_class_list=[4400, 1520, 560, 1680], gamma=1)
#     x = paddle.to_tensor(np.array([[0.1, 0.3, 0.5, 0.5]], dtype=np.float32))
#     label = paddle.to_tensor(np.array([1]))
#     loss = criterion(x, label)
#     print(loss)