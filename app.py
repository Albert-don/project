import logging
import os
import json
import configparser
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import redis
from ChatGPT_HKBU import HKBU_ChatGPT
from google.cloud.firestore_v1.base_query import FieldFilter

# 初始化Firebase
cred = credentials.Certificate('ServiceKey.json')
firebase_admin.initialize_app(cred)

# 获取Firestore数据库实例
db = firestore.client()

# Global variable for Redis connection
global redis1


def format_field(field_str):
    # 去除字符串两端的 'c(' 和 ')'，并以逗号分隔
    clean_str = field_str.strip('c(').rstrip(')')
    # 将字符串分割为列表
    items = clean_str.split('", "')
    # 去除列表中每个元素的双引号
    items = [item.strip('"') for item in items]
    return items


def get_message_from_cache(keyword):
    # 尝试从 Redis 缓存中获取消息
    cached_data = redis1.get(keyword)
    if cached_data:
        # 如果找到了缓存的消息，将其从 JSON 格式转换回来
        data = json.loads(cached_data)
        # 直接返回这个字典，它已经包含了关键词和回复
        return data
    return None



def save_message_to_cache(keyword, reply_message):
    # 构建包含关键词和回复的字典
    data_to_cache = {
        "keyword": keyword,
        "reply": reply_message
    }
    # 将字典转换为 JSON 格式字符串并保存到 Redis，这里假设关键词是唯一的标识
    redis1.set(keyword, json.dumps(data_to_cache), ex=3600)


def equiped_chatgpt(update, context):
    global chatgpt
    # 使用ChatGPT提取食物关键词
    print(update.message.text)
    food_keyword = chatgpt.submit("请帮我提取出食物的关键词,只返回食物英文单词,如果没有食物有关的关键词就只返回none" + ' ' + update.message.text)
    print("food keywords: ", food_keyword)
    if food_keyword and food_keyword != 'none':
        data = get_message_from_cache(food_keyword)
        if data:
            # 如果缓存中有数据，直接使用缓存的数据回复
            cached_recipe = data["keyword"]
            print('keyword from redis: ', cached_recipe)
            recipes = cached_recipe
            reply_cache = data["reply"]
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_cache)
        else:
            recipes = db.collection("recipes").where(filter=FieldFilter("Name", ">=", food_keyword)).order_by("Name").get()
            if recipes:
                for recipe in recipes:
                    recipe_data = recipes[0].to_dict()
                    # 使用format_field函数来格式化各个字段
                    # formatted_quantities = format_field(recipe_data.get('RecipeIngredientQuantities', ''))
                    # formatted_parts = format_field(recipe_data.get('RecipeIngredientParts', ''))
                    # formatted_instructions = format_field(recipe_data.get('RecipeInstructions', ''))

                    reply_message = f"Here's how you make {recipe_data.get('Name', 'a cake')}:\n"
                    reply_message += f"Ingredients (quantities): {recipe_data.get('RecipeIngredientQuantities', 'No quantities found.')}\n"
                    reply_message += f"Ingredients (parts): {recipe_data.get('RecipeIngredientParts', 'No parts found.')}\n"
                    reply_message += f"Instructions: {recipe_data.get('RecipeInstructions', 'No parts found')}\n"

                    reply = chatgpt.submit(reply_message + update.message.text + "将这些整理成一份recipe，给出原料合适的单位，根据文段中的对于菜谱的提问语言是中文还是英文给出对应语言答案，比如文段中有how can I make pork类似的提问，你就用英文回答其他语言一律给出英文回答，回答中只包含原料，用量和做法,不需要用sure之类的语言回应我的要求，NA代表适量")
                    save_message_to_cache(food_keyword, reply)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
                    return
    else:
        # 如果没有找到匹配的食谱或没有提取到食物关键词，就直接用ChatGPT回答原问题
        reply_message = chatgpt.submit(update.message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    updater = Updater(token=os.environ['ACCESS_TOKEN_TG'], use_context=True)
    dispatcher = updater.dispatcher
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # Initialize Redis connection
    global redis1
    redis1 = redis.Redis(
        # host=(config['REDIS']['HOST']),
        # password=(config['REDIS']['PASSWORD']),
        # port=int(config['REDIS']['REDISPORT'])
        host = (os.environ['HOST_REDIS']),
        password = (os.environ['PASSWORD_REDIS']),
        port = (os.environ['PORT_REDIS'])



    )

    # Logging configuration
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
