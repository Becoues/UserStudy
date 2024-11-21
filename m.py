from typing import List

import numpy as np
import torch

from models.ddsm import DDSM
from models.miasr import MIASR
from models.tools.utils import same_seeds, USE_CUDA



def load_model(file_name):
    rnn_params = {'rnn_type': 'GRU', 'hidden_size': 48, 'group_dim': 16, 'num_layers': 2, 'dropout': 0.3}
    if file_name == 'ddsm':
        ablation = {'gamma': False, 'gru_gate': False, 'aik': False, 'switching_cost': False}
    elif file_name == 'ddsm-ds':
        ablation = {'gamma': True, 'gru_gate': True, 'aik': True, 'switching_cost': False}
    elif file_name == 'miasr':
        pass
    else:
        raise ValueError(file_name)
    if 'ddsm' in file_name:
        model = DDSM(group_num=6, demand_num=60, embed_dim=128, mc_type=['store', 'sector', 'zone'], func_type='square',
                     rnn_params=rnn_params, feature_info=[[2], 1], index_path='./data/id2store.txt',
                     ablation=ablation, tau=1)
        save_path = f'model_log/ddsm/{file_name}/'
    else:
        model = MIASR(embedding_size=96, store_num=171, layer_num=2, max_length=30, block_num=4, dropout=0.4,
                      head_num=8, features="sector_zone")
        save_path = f'model_log/miasr/'
    device = torch.device('cuda:0' if USE_CUDA else 'cpu')
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
    # model_2 = load_model('ddsm-ds')
    model_2 = load_model('miasr')

    while True:
        same_seeds(100)
        # seq = [110, 93, 45]
        seq = [10, 18]
        # calculate_likelihood = True: 需要计算likelihood
        rec_1, log_likelihood = model_1.recommend(seq, calculate_likelihood=True)
        # rec_2 = model_2.recommend(seq)
        # rec_3 = model_3.recommend(seq, top_k=5)
        # print('DDSM:', rec_1)
        # print('DDSM-DS:', rec_2)
        # print('DDSM-SC:', rec_3)
        print(log_likelihood)
        # TODO: 计算得分，你也可以考虑呈现方式？
        percentile = get_percentile(log_likelihood, len(seq))  # ['0.34', '5.79', '33.57']
        print(percentile)
        rec_1 = model_1.generate_seq(seq)
        rec_2 = model_2.generate_seq(seq)
        # rec_3 = model_3.generate_seq(seq)
        print('DDSM:', rec_1)
        print('MIA-SR:', rec_2)
        break


def model_ddsm(seq):
    model = load_model('ddsm')
    rec_1 = model.generate_seq(seq)
    return rec_1

def model_miasr(seq):
    model = load_model('miasr')
    rec = model.generate_seq(seq)
    return rec

def model_get_likelihood(seq):
    model = load_model('ddsm')
    rec, log_likelihood = model.recommend(seq, calculate_likelihood=True)
    return log_likelihood


if __name__ == '__main__':
    main()
