import pandas as pd

file_path = "store_map.csv"
data = pd.read_csv(file_path)
data['floor'] = data['NodeID'].str.split('-').str[0].replace({'1S': '一楼', '2S': '二楼', '3S': '三楼', '4S': '四楼'})
new_data = data[data['IsDeleted'] == 0][['NodeID','StoreName', 'floor', 'CategoryName', 'idx']]
new_file_path = "data.csv"
new_data.to_csv(new_file_path, index=False)
Category = new_data['CategoryName'].unique()
print("完成")
