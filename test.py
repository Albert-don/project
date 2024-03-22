import os
import requests
import pandas as pd


videoid = input('input TikTok link > ')

# 提取视频ID
if "vm.tiktok.com" in videoid or "vt.tiktok.com" in videoid:
    videoid = requests.head(videoid, allow_redirects=True, timeout=5).url.split("/")[5].split("?", 1)[0]
else:
    videoid = videoid.split("/")[5].split("?", 1)[0]

# 初始化变量
t = 0
comments = []  # 用于存储所有评论
max_comments = 3000

# 开始抓取评论
while True:
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'referer': f'https://www.tiktok.com/@x/video/{videoid}',
        }

        response = requests.get(
            f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={videoid}&count=9999999&cursor={t}",
            headers=headers).json()

        comments.extend(response["comments"])
        t += 200  # 更新游标，与count值匹配

        if len(comments) >= max_comments:  # 检查是否已达到最大评论数
            comments = comments[:max_comments]  # 如果超过了3000条，截断列表
            break

    except TypeError:
        # 当没有更多评论时，终止循环
        break

# 将评论数据转换为DataFrame
df_comments = pd.DataFrame([comment['text'] for comment in comments], columns=['Comment'])

# 保存到CSV文件
# 保存到CSV文件，指定使用UTF-8编码
csv_filename = f'comments_{videoid}.csv'
df_comments.to_csv(csv_filename, index=False, encoding='utf-8-sig')
print(f'Saved {len(df_comments)} comments to {csv_filename}')

