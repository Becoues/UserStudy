from typing import List, Tuple, Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import List, Any, Tuple, Union
from models.tools.utils import TINY_NUM, positive_func, STORE_NUM, USE_CUDA
from typing import Any, List, Union, Tuple

class DDSM(nn.Module):
    def __init__(self, group_num, demand_num, embed_dim, mc_type, func_type, rnn_params,
                 feature_info, index_path, ablation, tau, batch_size=256):
        super().__init__()
        self.data_loader = None
        self.dataset = None
        self.opt = None
        self.seq_num = None
        self.group_num = group_num  # n_g
        self.demand_num = demand_num  # n_k
        self.embed_dim = embed_dim  # n_e
        self.mc_type = mc_type
        self.beta_dim = len(mc_type)
        self.func_type = func_type
        self.f = positive_func(self.func_type)
        self.rnn_params = rnn_params
        self.feature_info = feature_info
        self.batch_size = batch_size
        self.ablation = ablation
        self.tau = tau

        id2store = pd.read_csv(index_path).to_dict()['store']
        self.store_num = len(id2store)  # n_i = 171
        assert self.store_num == STORE_NUM

        self.osl = nn.Parameter(torch.randn(self.group_num, self.demand_num))  # Initial Optimum Stimulation Level, l_gk
        self.exit_osl = np.ones((self.group_num, 1))
        self.alpha = nn.Parameter(torch.randn(self.store_num, self.demand_num))  # a_jk
        if self.ablation['aik']:
            self.alpha.requires_grad_(False)
            nn.init.constant_(self.alpha, 0)
        self.embed_k = nn.Embedding(self.demand_num, self.embed_dim)
        self.embed_i = nn.Embedding(self.store_num + 1, self.embed_dim, padding_idx=self.store_num)
        self.w_arr = None
        self.w_arr_mean = None
        # self.w_arr = nn.Embedding(self.seq_num, self.group_num)  # the logit of group for shopping sequence
        # self.group_feature = {
        #     'discrete': [np.random.rand(self.group_num, num) for num in self.feature_info[0]],
        #     'continuous': np.random.randn(self.feature_info[1], self.group_num, 2),
        # }
        # self.group_feature['discrete'] = [x / np.sum(x, 1, keepdims=True) for x in self.group_feature['discrete']]
        # self.group_feature['continuous'][:, :, 1] = np.abs(self.group_feature['continuous'][:, :, 1])
        # self.group_feature['continuous'][:, :, 0] = self.group_feature['continuous'][:, :, 0] + 25
        # self.group_feature['continuous'][:, :, 1] = self.group_feature['continuous'][:, :, 1] * 5

        self.demand_decay = nn.Parameter(torch.randn(self.demand_num))
        self.mc_beta = nn.Parameter(torch.randn(self.beta_dim))
        if self.ablation['switching_cost']:
            self.mc_beta.requires_grad_(False)
            self.mc_beta *= 0
        with np.load('data/movement_convenience_exp_scaled.npz') as f:
            if len(self.mc_type) == 0:
                mc_factor = np.zeros((self.store_num + 1, self.store_num, 0))
            else:
                mc_factor = np.concatenate([np.expand_dims(f[k], -1) for k in self.mc_type], -1)
        self.register_buffer('mc_factor', torch.from_numpy(mc_factor).float())
        self.rnn_net = getattr(nn, self.rnn_params['rnn_type'])(
            input_size=self.embed_dim,
            hidden_size=self.rnn_params['hidden_size'],
            num_layers=self.rnn_params['num_layers'],
            batch_first=True,
            dropout=self.rnn_params['dropout'],
        )
        self.ln1 = nn.Linear(self.rnn_params['hidden_size'], self.embed_dim, bias=False)
        self.ln2 = nn.Linear(self.rnn_params['group_dim'], self.embed_dim, bias=False)
        self.group_embed = nn.Parameter(torch.randn(self.group_num, self.rnn_params['group_dim']))

        self.device = torch.device('cuda:0' if USE_CUDA else 'cpu')

    def forward(self, m, i, history):
        group_demand = (self.w_arr(m) / self.tau).softmax(1)  # batch * n_g
        demand_probs = self.generate_demand(history)  # batch * n_g * (n_k + 1)
        demand_store_probs = self.generate_store(history, i).unsqueeze(1)  # batch * 1 * (n_k + 1)
        store_prob = (demand_probs * demand_store_probs).sum(-1)  # batch * n_g
        log_prob = torch.log((group_demand * store_prob).sum(-1) + TINY_NUM)  # batch
        return log_prob

    def generate_rnn_weight(self, history):
        history_embed = self.embed_i(history)  # batch * max_length * embed_dim
        batch_size, max_length = history.shape
        output, _ = self.rnn_net(history_embed)  # batch * max_length * hidden_size
        # W(h || e_g) = W_1 h + W_2 e_g
        rnn_part = self.ln1(output).unsqueeze(1)  # batch * 1 * max_length * embed_dim
        group_part = self.ln2(self.group_embed)[None, :, None, :]  # 1 * n_g * 1 * embed_dim
        rnn_score = torch.relu(rnn_part + group_part)  # batch * n_g * max_length * embed_dim
        rnn_score = (rnn_score.unsqueeze(-2) * self.embed_k.weight).sum(-1)  # batch * n_g * max_length * n_k
        gate_weight = torch.sigmoid(rnn_score)  # batch * n_g * max_length * n_k
        if self.ablation['gru_gate']:
            gate_weight = gate_weight * 0 + 1
        mask = history.lt(self.store_num).reshape(batch_size, 1, -1, 1)  # batch * 1 * max_length * 1
        gate_weight = gate_weight * mask
        return gate_weight

    def predict(self, seq, e_disc, e_cont, calculate_likelihood):
        seq = seq.astype(int)
        batch_size, max_length = seq.shape
        assert max_length > 0
        seq = torch.from_numpy(seq).to(self.device)
        with torch.no_grad():
            self.eval()
            # =====demand_satiation_process=====
            demand_probs = self.generate_demand(seq, last=False)  # batch * n_g * (n_s + 1) * (n_k + 1)
            # =====store_choice_process=====
            # batch * (max_length + 1) * (n_i + 1) * (n_k + 1)
            demand_store_probs = self.generate_store(
                nn.functional.pad(seq, pad=[1, 0], value=self.store_num), last=False)
            i_probs = demand_store_probs[:, :-1][
                torch.arange(batch_size, device=self.device).unsqueeze(1),
                torch.arange(max_length, device=self.device), seq
            ]  # batch * max_length * (n_k + 1)
            store_probs = (
                    demand_probs[:, :, :-1, :] * i_probs.unsqueeze(1)).sum(-1)  # batch_size * n_g * max_length
            store_probs = store_probs.clamp(min=1e-10).log().sum(-1)  # batch_size * n_g
            # min_store_probs = store_probs.median(1, keepdims=True).values
            # seq_probs = (store_probs - min_store_probs).exp()
            # =====estimate g=====
            # g = seq_probs / seq_probs.sum(1, True)  # batch * n_g
            assert torch.allclose(self.w_arr_mean.sum(), torch.ones(1, device=self.w_arr_mean.device))
            store_probs = store_probs + self.w_arr_mean.log()
            g = store_probs.softmax(1)  # batch * n_g
            # print('demand_probs:', demand_probs.isnan().sum().item())
            # print('demand_store_probs:', demand_store_probs.isnan().sum().item())
            # print('store_probs:', store_probs.isnan().sum().item())
            # print('seq_probs:', seq_probs.isnan().sum().item())
            # print('seq_probs.max:', seq_probs.max().item(), '\tseq_probs.min:', seq_probs.min().item())
            # print('g:', g.isnan().sum().item(), '\tg.max:', g.max().item(), '\tg.min:', g.min().item())

        with torch.no_grad():
            self.eval()
            demand_probs = demand_probs[:, :, -1]  # batch_size * n_g * (n_k + 1)
            demand_probs = (demand_probs * g.unsqueeze(-1)).sum(1)  # batch_size * (n_k + 1)
            demand_probs = demand_probs.unsqueeze(1)  # dim of candidates_num, batch_size * 1 * (n_k + 1)

            demand_candidates_probs = demand_store_probs[:, -1]  # batch_size * (n_i + 1) * (n_k + 1)
            i_probs = (demand_probs * demand_candidates_probs).sum(-1)  # batch_size * (n_i + 1)
            # print('demand_probs:', demand_probs.isnan().sum().item())
            # print('demand_candidates_probs:', demand_candidates_probs.isnan().sum().item())
            # print('i_probs:', i_probs.isnan().sum().item())
            if calculate_likelihood:
                likelihood = store_probs.exp().sum(1)
        self.train()
        if calculate_likelihood:
            return i_probs.cpu().numpy(), likelihood.cpu().numpy()
        else:
            return i_probs.cpu().numpy()

    def generate_demand(self, history, last=True):
        """
        ========== Demand Satiation Process ==========

        Given group g and sequence **s**, calculate the probability of generating demand k
                    p(k|s, g) = softmax(theta)
        :param history: shopping sequence **s**
        :param last: boolean, the demand in the last time step
        :return: demand_probs, (batch, n_g, 1 or max_length, n_k + 1). demand_probs[:, g, n, k] = p(k| s^{n-1}, g)
        """
        osl, alpha = self.f(self.osl), self.f(self.alpha)
        batch_size, max_length = history.shape

        alpha = nn.functional.pad(alpha, [0, 0, 0, 1])
        rnn_weight = self.generate_rnn_weight(history)  # batch * n_g * max_length * n_k
        gamma = torch.sigmoid(self.demand_decay)  # n_k
        if self.ablation['gamma']:
            gamma = gamma * 0 + 1
        if last:
            seq_length = torch.lt(history, self.store_num).sum(1, True)  # batch * 1
            gamma = gamma[:, None, None]  # n_k * 1 * 1
            exponent = torch.clamp(
                seq_length - torch.arange(1, max_length + 1, device=self.device), 0)  # batch * max_length
            demand_decay = torch.pow(gamma, exponent)  # n_k * batch * max_length
            demand_decay = demand_decay.transpose(0, 1).transpose(1, 2)  # batch * max_length * n_k
            theta = osl - ((alpha[history] * demand_decay).unsqueeze(1) * rnn_weight).sum(-2)  # batch * n_g * n_k
        else:
            asl = [torch.zeros(batch_size, self.group_num, self.demand_num, device=self.device)]
            for tau in range(max_length):
                asl.append(
                    asl[-1] * gamma + (
                            alpha[history[:, tau]].unsqueeze(1)  # batch_size * 1 * n_k
                            * rnn_weight[:, :, tau]  # batch_size * n_g * n_k
                    )
                )
            asl = torch.stack(asl, dim=2)  # batch * n_g * (max_length + 1) * n_k
            theta = osl.unsqueeze(1) - asl  # batch * n_g * (max_length + 1) * n_k
        theta = torch.nn.functional.pad(theta, pad=[0, 1], value=1)  # add p(k+)
        theta = theta - (theta < 0) * (1 / TINY_NUM)
        demand_probs = torch.softmax(theta, -1)
        # demand_probs = demand_probs * (seq >= 0).reshape(batch_size, 1, max_length, 1)
        return demand_probs

    def generate_store(self, history, i=None, last=True):
        """
        ========== Store Choice Process ==========

        Given demand k and sequence s, calculate the probability of visiting store i
                    p(i|s, k) = softmax(e_i e_k - beta * mc_factor)
        :param history: shopping sequence **s**
        :param i: target store
        :param last: boolean, the store choice in the last time step
        :return: seq_probs, (batch_size, n_s, n_k) or (batch_size, n_i, n_k).
                 seq_probs[:, n, k] = p(i_n| s^{n-1}, k) or seq_probs[:, i, k] = p(i| s, k)
        """
        batch_size = history.shape[0]
        b_ik = torch.mm(self.embed_i.weight[:-1], self.embed_k.weight.t())  # n_i * n_k
        if last:
            seq_length = torch.lt(history, self.store_num).sum(1)
            # i is i_1  ->  seq_length = 0  ->  last = history[batch, 0 - 1] = self.demand_num (padding)
            last_i = history[range(batch_size), seq_length - 1]
            mc_factor = self.mc_factor[last_i]  # batch * n_i * beta_dim
            b_ik = b_ik[None, :, :]
        else:
            mc_factor = self.mc_factor[history]  # batch * (max_length + 1) * n_i * beta_dim
            b_ik = b_ik[None, None, :, :]
        store_probs = b_ik - (mc_factor * self.mc_beta).sum(-1, True)  # batch * n_i * n_k
        store_probs = torch.softmax(store_probs, -2)
        pad_store_probs = nn.functional.pad(store_probs, [0, 1, 0, 1])  # batch * (n_i + 1) * (n_k + 1)
        if last:
            seq_probs = pad_store_probs[torch.arange(batch_size), i]  # batch * (n_k + 1)
            seq_probs[i == self.store_num, -1] = seq_probs[i == self.store_num, -1] + 1  # p(i+|k+) = 1
        else:
            pad_store_probs[:, :, -1, -1] = pad_store_probs[:, :, -1, -1] + 1
            seq_probs = pad_store_probs  # batch * (max_length + 1) * (n_i + 1) * (n_k + 1)
        return seq_probs

    def load_model(self, save_path, step):
        state_dict = torch.load(f'{save_path}net_{step}.pt')
        self.load_state_dict(state_dict)
        print(f'Loading net from {save_path}net_{step}.pt')
        # self.register_buffer('w_arr', torch.load(f'{save_path}w_arr_{step}.pt').softmax(1).mean(0, True))
        # self.w_arr_mean = (torch.load(f'{save_path}w_arr_{step}.pt') / self.tau).softmax(1).mean(0, True).to(self.device)
        self.w_arr_mean = torch.load(f'{save_path}w_arr_mean_{step}.pt').to(self.device)

    def recommend(
            self, seq: List[int], top_k: int = 5, calculate_likelihood: bool = False
    ) -> Union[Tuple[List[Any], float], List[Any]]:
        #-> tuple[list[Any], float] | list[Any]:
        """
        :param seq: 逛店轨迹的index，例如[42, 6, 12]
        :param top_k: 推荐列表长度
        :param calculate_likelihood: 是否计算似然
        :return: rec: 推荐列表的index，例如[9, 46, 2, 1, 54]
        :return: likelihood: seq的似然函数
        """
        result = self.predict(np.array([seq]), None, None, calculate_likelihood)  # 计算所有店铺的推荐概率
        if calculate_likelihood:
            i_probs = result[0][0][:STORE_NUM]
        else:
            i_probs = result[0][:STORE_NUM]
        candidates = np.setdiff1d(range(STORE_NUM), seq).tolist()  # 候选集：目前选为未逛过的店铺
        candidate_score = i_probs[candidates]
        top_indices = candidate_score.argsort()[-top_k:][::-1]  # 取最大的top_k个索引，按概率降序排列
        rec = [candidates[idx] for idx in top_indices]
        if calculate_likelihood:
            likelihood = float(result[1][0])
            return rec, np.log(likelihood)
        else:
            return rec