from typing import List
from typing import Any, List, Union, Tuple   
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch_geometric.nn import LightGCN

from models.tools.utils import STORE_NUM, USE_CUDA


def masked_softmax(tensor, mask, dim, eps=1e-20):
    out = (tensor * mask).softmax(dim)
    out = out * mask
    out = out / (out.sum(dim, True) + eps)
    return out


class AttentionBlock(nn.Module):
    def __init__(self, embedding_size, output_dim=None):
        super(AttentionBlock, self).__init__()
        self.embedding_size = embedding_size
        self.output_dim = self.embedding_size if output_dim is None else output_dim
        self.query_weight = nn.Linear(self.embedding_size, self.output_dim, bias=False)
        self.key_weight = nn.Linear(self.embedding_size, self.output_dim, bias=False)
        self.value_weight = nn.Linear(self.embedding_size, self.output_dim, bias=False)

    def forward(self, x, mask):
        query = self.query_weight(x)
        key = self.key_weight(x)
        value = self.value_weight(x)

        attention_score = torch.matmul(query, key.transpose(1, 2)) / (self.output_dim ** 0.5)
        attention_weight = masked_softmax(attention_score, mask, -1)
        # attention_weight = torch.softmax(attention_score, -1)

        output = torch.matmul(attention_weight, value)
        return output


class FeedForwardNet(nn.Module):
    def __init__(self, embedding_size, hidden_dim=None, act_fn='ReLU'):
        super(FeedForwardNet, self).__init__()
        self.embedding_size = embedding_size
        self.hidden_dim = embedding_size if hidden_dim is None else hidden_dim
        self.act_fn = act_fn

        self.ln_layer1 = nn.Linear(self.embedding_size, self.hidden_dim)
        self.ln_layer2 = nn.Linear(self.hidden_dim, self.embedding_size)

    def forward(self, x):
        output = getattr(nn, self.act_fn)()(self.ln_layer1(x))
        output = self.ln_layer2(output)
        return output


class BERTBlock(nn.Module):
    def __init__(self, embedding_size, dropout, head_num, act_fn='GELU'):
        super(BERTBlock, self).__init__()
        self.embedding_size = embedding_size
        self.dropout = dropout
        self.head_num = head_num

        self.dropout_layer = nn.Dropout(self.dropout)

        self.attn_norm = nn.LayerNorm(self.embedding_size)
        self.attn = nn.ModuleList([
            AttentionBlock(self.embedding_size, self.embedding_size // self.head_num)
            for _ in range(self.head_num)
        ])
        self.mh_layer = nn.Linear(self.embedding_size, self.embedding_size, bias=False)

        self.ffn_norm = nn.LayerNorm(self.embedding_size)
        self.ffn = FeedForwardNet(self.embedding_size, self.embedding_size * 4, act_fn)

    def forward(self, h, mask):
        # A^{l - 1} = LN(H^{l - 1} + Dropout(MH(H^{l - 1})))
        residual_h = h
        attn_output = [self.attn[i](h, mask) for i in range(self.head_num)]
        head_stack = torch.cat(attn_output, -1)
        mh_output = self.mh_layer(head_stack)
        h = residual_h + self.dropout_layer(mh_output)
        a = self.attn_norm(h)

        # H^l = LN(A^{l - 1} + Dropout(PFFN(A^{l - 1})))
        residual_a = a
        ffn_output = self.ffn(a) * mask[:, -1].unsqueeze(-1)
        a = residual_a + self.dropout_layer(ffn_output)
        output = self.ffn_norm(a)

        return output


class MIASR(nn.Module):
    def __init__(self, embedding_size, store_num, layer_num, max_length, block_num, dropout, head_num, features):
        super(MIASR, self).__init__()
        self.embedding_size = embedding_size
        self.store_num = store_num
        self.layer_num = layer_num
        self.max_length = max_length
        self.block_num = block_num
        self.dropout = dropout
        self.head_num = head_num
        self.features = features.split('_')  # 'sector_zone'

        id2store = pd.read_csv('./data/id2store.txt').set_index('index')
        offset = self.store_num
        edge_index = []
        for feat in self.features:
            # store: 0~170, sector: 171~198, zone: 199~206
            # offset: 171 -> 171 + (27 + 1) = 199 -> 199 + (7 + 1) = 207
            tmp = []
            for i in range(self.store_num):
                if i == 171:  # TODO 1
                    assert i not in id2store[feat]
                    tmp.append(id2store[feat].max() + 1 + offset)
                else:
                    tmp.append(id2store[feat][i] + offset)
                edge_index.append([i, tmp[-1]])
                edge_index.append([tmp[-1], i])
            self.register_buffer(f'{feat}_map', torch.LongTensor(tmp + [offset]))  # the last is used for padding
            # self.register_buffer(f'{feat}_map', torch.LongTensor([
            #     id2store[feat][i] + offset for i in range(self.store_num)
            # ] + [offset]))  # the last is used for padding
            offset += len(set(getattr(self, f'{feat}_map').tolist()))
        self.register_buffer('edge_index', torch.LongTensor(edge_index).t())
        # self.item_embedding = nn.Embedding(offset + 1, self.embedding_size, padding_idx=-1)
        self.gcn_layer = LightGCN(num_nodes=offset + 1, embedding_dim=self.embedding_size, num_layers=self.layer_num)

        self.position_embed = nn.Embedding(self.max_length, self.embedding_size)
        self.transformer = nn.ModuleList([
            BERTBlock(self.embedding_size, self.dropout, self.head_num, act_fn='ReLU') for _ in range(self.block_num)
        ])

        self.attention_w = nn.ModuleList([
            nn.Linear(self.embedding_size, self.embedding_size) for _ in range(1 + len(self.features))
        ])
        self.attention_q = nn.ModuleList([
            nn.Linear(self.embedding_size, 1) for _ in range(1 + len(self.features))
        ])
        self.sigma = nn.Parameter(torch.ones(len(self.features) + 1))

        self.device = torch.device('cuda:0' if USE_CUDA else 'cpu')

    def forward(self, seq, target, flatten=True):
        # Embedding Layer
        # Graph Convolution Layer (LightGCN)
        item_embedding = self.gcn_layer.get_embedding(self.edge_index)
        # seq_embed = self.item_embedding(seq)
        # feature_seq_embed = {
        #     feat: self.item_embedding(getattr(self, f'{feat}_map')[seq]) for feat in self.features
        # }
        seq_embed = item_embedding[seq]
        feature_seq_embed = {
            feat: item_embedding[getattr(self, f'{feat}_map')[seq]] for feat in self.features
        }

        # Sequential Encoder
        mask = self.get_attention_mask(seq)
        pos_embed = self.position_embed.weight.unsqueeze(0)
        seq_embed = seq_embed + pos_embed  # batch * max_length * embedding_size
        feature_seq_embed = {
            feat: v + pos_embed for feat, v in feature_seq_embed.items()
        }

        for i in range(self.block_num):
            seq_embed = self.transformer[i](seq_embed, mask)
            feature_seq_embed = {
                feat: self.transformer[i](v, mask) for feat, v in feature_seq_embed.items()
            }

        # batch * max_length * (f + 1) * embedding_size
        agg_embed = torch.stack([seq_embed] + list(feature_seq_embed.values()), dim=2)
        task_preference = []
        for i in range(1 + len(self.features)):
            alpha = torch.relu(self.attention_w[i](agg_embed))  # batch * max_length * (f + 1) * embedding_size
            alpha = self.attention_q[i](alpha)  # batch * max_length * (f + 1) * 1
            alpha = alpha.softmax(2)
            task_preference.append(
                (alpha * agg_embed).sum(2)  # batch * max_length * embedding_size
            )
        task_preference = torch.stack(task_preference, dim=2)  # batch * max_length * (f + 1) * embedding_size

        mask = torch.lt(seq, self.store_num)
        task_preference = task_preference * mask[:, :, None, None]
        # target_embed = self.item_embedding(target)  # batch * max_length * (1 + |C|) * embedding_size
        # target_embed = [target_embed] + [
        #     self.item_embedding(getattr(self, f'{feat}_map')[target]) for feat in self.features
        # ]
        target_embed = item_embedding[target]  # batch * max_length * (1 + |C|) * embedding_size
        target_embed = [target_embed] + [
            item_embedding[getattr(self, f'{feat}_map')[target]] for feat in self.features
        ]
        target_embed = torch.stack(target_embed, -2)  # batch * max_length * (1 + neg) * (f + 1) * embedding_size
        if flatten:
            task_preference = task_preference[mask]  # batch * (f + 1) * embedding_size
            target_embed = target_embed[mask]  # batch * (1 + neg) * (f + 1) * embedding_size
        return task_preference, target_embed

    def predict(self, seq, e_disc, e_cont):
        seq = seq[:, -self.max_length:]
        batch_size = len(seq)
        pad = np.ones((batch_size, self.max_length - seq.shape[1])) * self.store_num
        seq = np.hstack((pad, seq))
        seq = torch.from_numpy(seq).long().to(self.device)
        target = torch.arange(self.store_num).unsqueeze(0).repeat(batch_size, 1).to(self.device)
        self.eval()
        with torch.no_grad():
            seq_embed, target_embed = self.forward(seq, target, flatten=False)
            seq_embed = seq_embed[:, -1, 0]  # batch * embedding_size
            target_embed = target_embed[:, :, 0]  # # batch * item_num * embedding_size
            i_probs = (target_embed * seq_embed.unsqueeze(-2)).sum(-1)
            i_probs = i_probs.softmax(-1)
        return i_probs.cpu().numpy()

    def get_attention_mask(self, seq, causality=True):
        mask = torch.lt(seq, self.store_num).float()
        # if seq is [<pad>, <pad>, i1, i2, i3], then the mask is
        # [0, 0, 0, 0, 0],
        # [0, 0, 0, 0, 0],
        # [0, 0, 1, 1, 1],
        # [0, 0, 1, 1, 1],
        # [0, 0, 1, 1, 1],
        mask = torch.matmul(mask.unsqueeze(-1), mask.unsqueeze(-2))
        if causality:
            # mask then transforms into
            # [0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 0],
            # [0, 0, 1, 0, 0],
            # [0, 0, 1, 1, 0],
            # [0, 0, 1, 1, 1],
            one_in_tri = torch.tril(torch.ones(self.max_length, self.max_length)).unsqueeze(0).to(self.device)
            mask = mask * one_in_tri
        return mask

    def load_model(self, save_path, step):
        self.load_state_dict(torch.load(f'{save_path}net_{step}.pt'))
        print(f'Loading parameters from {save_path}net_{step}.pt')

    def recommend(
            self, seq: List[int], top_k: int = 5, candidates=None
    ) -> Union[tuple[list[int], float], list[int]]:
        """
        :param seq: 逛店轨迹的index，例如[42, 6, 12]
        :param top_k: 推荐列表长度
        :param candidates候选集，如果为None则考虑未出现过的店铺
        :return: rec: 推荐列表的index，例如[9, 46, 2, 1, 54]
        :return: likelihood: seq的似然函数
        """
        result = self.predict(np.array([seq]), None, None)  # 计算所有店铺的推荐概率
        if candidates is None:
            i_probs = result[0][:STORE_NUM]
            candidates = np.setdiff1d(range(STORE_NUM), seq).tolist()  # 候选集：目前选为未逛过的店铺
        else:
            i_probs = result[0]
        candidate_score = i_probs[candidates]
        top_indices = candidate_score.argsort()[-top_k:][::-1]  # 取最大的top_k个索引，按概率降序排列
        rec = [candidates[idx] for idx in top_indices]
        return rec

    def generate_seq(self, seq, unique=True):
        # max_length = 7 - len(seq)
        sample_set = {
            5: 24294, 6: 24920, 7: 16813, 8: 11389, 9: 7615, 10: 5377, 11: 3753, 12: 2728, 13: 1845,
            14: 1440, 15: 1028, 16: 783, 17: 575, 18: 431, 19: 277, 20: 239, 21: 171, 22: 150, 23: 104,
            24: 73, 25: 57, 26: 39, 27: 47, 28: 36, 29: 18, 30: 15
        }
        sample_set = {k: v / sum(sample_set.values()) for k, v in sample_set.items()}
        # max_length的随机性仅受`seq`影响，故使用np.random.default_rng而不影响整体的种子
        rng = np.random.default_rng(seed=int(''.join(map(str, seq))))
        max_length = rng.choice(len(sample_set), p=list(sample_set.values())) + 5 - len(seq)

        store_num = STORE_NUM
        pred_seq = list()
        candidates = None
        while candidates is None or len(candidates) > 0:
            if len(pred_seq) >= max_length:
                break
            if unique:
                candidates = np.setdiff1d(range(store_num), seq + pred_seq).tolist()
            else:
                last_store = pred_seq[-1] if len(pred_seq) else seq[-1]
                candidates = list(range(0, last_store)) + list(range(last_store + 1, store_num))
            next_store = self.recommend(seq + pred_seq, top_k=1, candidates=candidates)[0]
            pred_seq.append(next_store)
        return pred_seq
