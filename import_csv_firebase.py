import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Initialize Firebase
cred = credentials.Certificate("serviceKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

food_keyword = "vanilla cake"
recipes = db.collection("recipes").where(filter=FieldFilter("Name", ">=", food_keyword)).order_by("Name").get()
if recipes:
    first_recipe = recipes[0].to_dict()
    print(first_recipe)
else:
    print("No recipes found matching the keyword.")

# 读取CSV文件并上传数据到Firestore
# def upload_data_from_csv(csv_file_path, collection_name):
#     with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#
#         for row in csv_reader:
#             # 使用'RecipeId'作为文档ID
#             document_id = row['Name']
#             # 将行数据上传到指定的集合中
#             db.collection(collection_name).document(document_id).set(row)


# 调用函数，上传数据
# upload_data_from_csv('recipe.csv', 'recipes')

# import pandas as pd
#
# # 读取CSV文件
# df = pd.read_csv('recipes.csv')
#
# # 重置RecipeId为从1开始的连续整数
# # df['RecipeId'] = range(1, len(df) + 1)
# df['Name'] = df['Name'].str.lower()
# # 保存更改后的CSV文件
# df.to_csv('recipe2.csv', index=False)
