import pandas as pd

file_path = "store_map.csv"
data = pd.read_csv(file_path)
data['floor'] = data['NodeID'].str.split('-').str[0].replace({'1S': '一楼', '2S': '二楼', '3S': '三楼', '4S': '四楼'})
new_data = data[:][['NodeID','StoreName', 'floor', 'CategoryName', 'idx']]


file_path2 = "store.csv"
data2 = pd.read_csv(file_path2)
data2['brandName'] = data2['brandName'].str.strip('"')
new_data['StoreName'] = data['StoreName'].astype(str)
new_data['plaza_unitid'] = " "
data2['brandName'] = data2['brandName'].astype(str)
brand_to_unitid = data2.set_index('brandName')['plazaUnitid'].to_dict()
new_data['plaza_unitid'] = new_data['StoreName'].map(brand_to_unitid)


idx_to_zoom = {
    0: '1S', 1: '3S', 2: '3S', 3: '3N', 4: '3S', 5: '3S', 6: '1S', 7: '1S', 8: '1S', 9: '1S',
    10: '2S', 11: '3N', 12: '3S', 13: '1N', 14: '1N', 15: '2S', 16: '2S', 17: '2S', 18: '3S',
    19: '3N', 20: '3N', 21: '3S', 22: '1S', 23: '1S', 24: '1N', 25: '2S', 26: '2S', 27: '2S',
    28: '2S', 29: '2N', 30: '2S', 31: '2S', 32: '2S', 33: '2S', 34: '2S', 35: '3N', 36: '3S',
    37: '1S', 38: '2S', 39: '2S', 40: '2N', 41: '3S', 42: '3N', 43: '3N', 44: '1N', 45: '1N',
    46: '1S', 47: '3S', 48: '1S', 49: '2S', 50: '2N', 51: '3S', 52: '3S', 53: '3S', 54: '3S',
    55: '3N', 56: '3S', 57: '1S', 58: '1N', 59: '1N', 60: '4S', 61: '2N', 62: '3S', 63: '1S',
    64: '3S', 65: '3S', 66: '3S', 67: '3S', 68: '3S', 69: '4S', 70: '3N', 71: '3S', 72: '4S',
    73: '1S', 74: '3S', 75: '2N', 76: '2N', 77: '2N', 78: '2S', 79: '2S', 80: '1S', 81: '2N',
    82: '2S', 83: '3S', 84: '3N', 85: '1S', 86: '1N', 87: '3N', 88: '4N', 89: '3S', 90: '1S',
    91: '4S', 92: '2S', 93: '1N', 94: '2S', 95: '1N', 96: '1N', 97: '2N', 98: '2N', 99: '2S',
    100: '3S', 101: '1N', 102: '2S', 103: '3N', 104: '3N', 105: '4S', 106: '2S', 107: '2N',
    108: '3N', 109: '2S', 110: '1S', 111: '1S', 112: '4N', 113: '2S', 114: '2S', 115: '2S',
    116: '3N', 117: '1S', 118: '1S', 119: '2N', 120: '2N', 121: '4S', 122: '1N', 123: '4S',
    124: '4S', 125: '4S', 126: '2N', 127: '4S', 128: '4S', 129: '1S', 130: '1S', 131: '4N',
    132: '2N', 133: '4S', 134: '1N', 135: '1S', 136: '3N', 137: '2N', 138: '3S', 139: '2S',
    140: '4N', 141: '4S', 142: '1N', 143: '1N', 144: '4N', 145: '1N', 146: '3N', 147: '3N',
    148: '3N', 149: '4N', 150: '2S', 151: '1N', 152: '3S', 153: '1S', 154: '4N', 155: '4N',
    156: '3S', 157: '4S', 158: '2N', 159: '2N', 160: '2N', 161: '4N', 162: '3S', 163: '4N',
    164: '3N', 165: '3N', 166: '2S', 167: '4N', 168: '4S', 169: '4S', 170: '4N'
}
idx_to_zoom_df = pd.DataFrame({'idx': new_data.index})
idx_to_zoom_df['zoom'] = idx_to_zoom_df['idx'].map(idx_to_zoom)
new_data = pd.merge(new_data, idx_to_zoom_df, left_index=True, right_on='idx')
new_data['zoom'] = new_data['zoom'].str[1].replace({'S': '北区', 'N': '南区'})
new_file_path = "data.csv"
new_data.to_csv(new_file_path, index=False)
SiteID = new_data['plaza_unitid'].unique()
Category = new_data['CategoryName'].unique()



print("完成")
