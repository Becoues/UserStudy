import pandas as pd

file_path = "store_map-v2.csv"
data = pd.read_csv(file_path)

data['floor'] = data['NodeID'].str.split('-').str[0].replace({'1S': '一楼', '2S': '二楼', '3S': '三楼', '4S': '四楼'})
new_data = data[:][['NodeID','StoreName', 'floor', 'new_category', 'idx',"PlazaUnitID"]]

store_data = pd.read_csv('store.csv')
store_data.rename(columns={'storeName': 'StoreName'}, inplace=True)
new_data = pd.merge(new_data, store_data[['StoreName', 'plazaName']], on='StoreName', how='left')
new_data.rename(columns={'plazaName': 'shoptime'}, inplace=True)
new_data = new_data.drop_duplicates(subset='StoreName', keep='first')

# file_path2 = "store.csv"
# data2 = pd.read_csv(file_path2)
# data2['brandName'] = data2['brandName'].str.strip('"')
# new_data['StoreName'] = data['StoreName'].astype(str)
# new_data['plaza_unitid'] = " "
# data2['brandName'] = data2['brandName'].astype(str)
# brand_to_unitid = data2.set_index('brandName')['plazaUnitid'].to_dict()
# new_data['plaza_unitid'] = new_data['StoreName'].map(brand_to_unitid)


idx_to_plaza = {0: '1026', 1: '3030A', 2: '3017', 3: '30,583,059', 4: '3019', 5: '3021', 6: '1012A,1012B', 7: '1005A,1005B', 8: '1057', 9: '10581059', 10: '2057', 11: '3051', 12: '3002', 13: '1051B', 14: '次主力店1', 15: '2017B', 16: '2008', 17: '2056', 18: '3035', 19: '娱乐楼3FA', 20: '3038A', 21: '3028', 22: '1006A', 23: '1011', 24: '10291030', 25: '2019A', 26: '2017A', 27: '2018', 28: '2020', 29: '2029A', 30: '2019B', 31: '2015', 32: '2011', 33: '2002', 34: '2003', 35: '3057', 36: '30,113,012', 37: '1009', 38: '2013', 39: '2058', 40: '2031', 41: '3025', 42: '3050', 43: '3061', 44: '10271028', 45: '1039', 46: '1003B', 47: '3020', 48: '1007A', 49: '2021A', 50: '2030B', 51: '3023', 52: '3026', 53: '3027', 54: '3031', 55: '3039B', 56: '3030B', 57: '1006B', 58: '1053', 59: '1052A', 60: '4006B', 61: '娱乐楼2FA', 62: '30,323,033', 63: '1018B', 64: '3022', 65: '3010', 66: '30,053,006', 67: '3003', 68: '3008', 69: '4001', 70: '3056', 71: '3018', 72: '4003B', 73: '1008', 74: '3009', 75: '2032A', 76: '2039', 77: '2050', 78: '2009', 79: '2006', 80: '1025', 81: '2029B', 82: '2016', 83: '3029', 84: '3039A', 85: '1003A', 86: '1055', 87: '3038B', 88: '4027', 89: '3036', 90: '1018A', 91: '4009B', 92: '2026', 93: '1037', 94: '2005', 95: '1002,2055B', 96: '10,351,036', 97: '2033', 98: '2037', 99: '2001', 100: '3001A,3001B', 101: '1032', 102: '2022A', 103: '3052', 104: '3053B', 105: '4017', 106: '2021B', 107: '2028B', 108: '3060', 109: '2010', 110: '1017', 111: '1021,1022A', 112: '4020B', 113: '2022B', 114: '2023', 115: '2025B', 116: '3053A', 117: '1013', 118: '1015A', 119: '2036', 120: '2028A', 121: '40,114,012', 122: '1033', 123: '4010A,4010B', 124: '4003A', 125: '4006A', 126: '2035', 127: '4008', 128: '4007', 129: '1007B', 130: '1010B,1010A', 131: '4018', 132: '2030A', 133: '4005', 134: '1056', 135: '1022B,1023', 136: '3062', 137: '2055B,1002', 138: '3016', 139: '2012', 140: '4022', 141: '4002', 142: '1031', 143: '1050', 144: '4019A', 145: '1038', 146: '3067', 147: '3066', 148: '3063B', 149: '4025B', 150: '2007', 151: '1051A', 152: '3007', 153: '1016', 154: '4021A', 155: '4019B,4019C', 156: '3015', 157: '4013', 158: '2027', 159: '2032B', 160: '2038', 161: '4026B', 162: '3013', 163: '娱乐楼4FA', 164: '3055', 165: '3063A', 166: '2025A', 167: '4025A', 168: '4015A', 169: '4016', 170: '4026A'}
new_data['plaza_unitid'] = new_data['idx'].map(idx_to_plaza)


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
SiteID = new_data['PlazaUnitID'].unique()
Category = new_data['new_category'].unique()
Storename = new_data['StoreName'].unique()
