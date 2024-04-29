from typing import List

import numpy as np
import torch

from models.ddsm import DDSM
from models.tools.utils import same_seeds, USE_CUDA


def load_model(file_name):
    rnn_params = {'rnn_type': 'GRU', 'hidden_size': 48, 'group_dim': 16, 'num_layers': 2, 'dropout': 0.3}
    if file_name == 'ddsm':
        ablation = {'gamma': False, 'gru_gate': False, 'aik': False, 'switching_cost': False}
    elif file_name == 'ddsm-ds':
        ablation = {'gamma': True, 'gru_gate': True, 'aik': True, 'switching_cost': False}
    else:
        raise ValueError(file_name)
    model = DDSM(group_num=6, demand_num=60, embed_dim=128, mc_type=['store', 'sector', 'zone'], func_type='square',
                 rnn_params=rnn_params, feature_info=[[2], 1], index_path='./data/id2store.txt',
                 ablation=ablation, tau=1)
    device = torch.device('cuda:0' if USE_CUDA else 'cpu')
    save_path = f'model_log/ddsm/{file_name}/'
    model.load_model(save_path, 'final')
    model.to(device)
    return model


def get_percentile(likelihood: float, seq_length: int) -> List[str]:
    result = np.load('./data/log_likelihood_np.npy', allow_pickle=True).item()
    percentile = (result[f'first-{seq_length}'] < likelihood).mean()
    result = [
        # 原始百分比（0～1）、(百分比) ** 0.5 * 10 （0～10）、百分比 * 100
        percentile, np.sqrt(percentile) * 10, percentile * 100
    ]
    return [f'{item:.2f}' for item in result]


def main():
    model_1 = load_model('ddsm')
    model_2 = load_model('ddsm-ds')

    while True:
        same_seeds(100)
        seq = [73, 37, 130, 23, 6]
        # calculate_likelihood = True: 需要计算likelihood
        rec_1, log_likelihood = model_1.recommend(seq, calculate_likelihood=True)
        rec_2 = model_2.recommend(seq)
        print('Method 1:', rec_1)
        print('Method 2:', rec_2)
        print(log_likelihood)
        # TODO: 计算得分，你也可以考虑呈现方式？
        percentile = get_percentile(log_likelihood, len(seq))  # ['0.92', '9.58', '91.84']
        print(percentile)
        break

def model_ddsm(seq):
    model = load_model('ddsm')
    rec = model.recommend(seq,top_k=10,calculate_likelihood=False)
    return rec

def model_ddsmds(seq):
    model = load_model('ddsm-ds')
    rec = model.recommend(seq,top_k=10)
    return rec

def model_get_likelihood(seq):
    model = load_model('ddsm')
    rec, log_likelihood = model.recommend(seq, calculate_likelihood=True)
    return log_likelihood

