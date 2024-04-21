import random

import numpy as np
import torch

TINY_NUM = 1e-20
STORE_NUM = 171
USE_CUDA = torch.cuda.is_available()


def same_seeds(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # if you are using multi-GPU.
    np.random.seed(seed)  # Numpy module.
    random.seed(seed)  # Python random module.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def positive_func(f_type):
    if f_type == 'abs':
        return general_abs
    elif f_type == 'exp':
        return general_exp
    elif f_type == 'square':
        return lambda x: x ** 2
    else:
        raise ValueError(f'Not implemented type: {f_type}')


def general_abs(x):
    if isinstance(x, np.ndarray):
        return np.abs(x)
    elif isinstance(x, torch.Tensor):
        return torch.abs(x)
    else:
        raise ValueError(f'Not implemented type: {type(x)}')


def general_exp(x):
    if isinstance(x, np.ndarray):
        return np.exp(x)
    elif isinstance(x, torch.Tensor):
        return torch.exp(x)
    else:
        raise ValueError(f'Not implemented type: {type(x)}')
