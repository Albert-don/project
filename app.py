import logging
import os
import re
import json
import configparser
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import redis
from ChatGPT_HKBU import HKBU_ChatGPT
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate('ServiceKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

global redis1

def format_str(foodname):
    remove = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    output = "".join(char if char not in remove else " " for char in foodname)
    output = " ".join(output.split())
    return output


def get_cache_info(keyword):
    cached_data = redis1.get(keyword)
    if cached_data:
        data = json.loads(cached_data)
        return data
    return None

def save_to_redis(keyword, reply_message):
    data_to_cache = {
        "keyword": keyword,
        "reply": reply_message
    }
    redis1.set(keyword, json.dumps(data_to_cache), ex=3600)

def equiped_chatgpt(update, context):
    global chatgpt
    print(update.message.text)
    food_keyword1 = chatgpt.submit("请帮我提取出食物的关键词,只返回食物英文单词,不要加标点符号;如果没有食物有关的关键词就只返回none,注意没有一定是回答none!" + ' ' + update.message.text)
    print("food keywords: ", food_keyword1)
    food_keyword = format_str(food_keyword1)
    if food_keyword and 'none' not in food_keyword:
        data = get_cache_info(food_keyword)
        if data:
            cached_recipe = data["keyword"]
            print('keyword from redis: ', cached_recipe)
            recipes = cached_recipe
            reply_cache = data["reply"]
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_cache)
        else:
            recipes = db.collection("recipes").where(filter=FieldFilter("Name", ">=", food_keyword)).order_by("Name").get()
            if recipes:
                recipe_data = recipes[0].to_dict()
                reply_message = f"Here's how you make {recipe_data.get('Name')}:\n"
                reply_message += f"Ingredients (quantities): {recipe_data.get('RecipeIngredientQuantities')}\n"
                reply_message += f"Ingredients (parts): {recipe_data.get('RecipeIngredientParts')}\n"
                reply_message += f"Instructions: {recipe_data.get('RecipeInstructions')}\n"

                reply = chatgpt.submit(reply_message + update.message.text + "将这些整理成一份recipe，给出原料合适的单位，根据文段中的对于菜谱的提问语言是中文还是英文给出对应语言答案，比如文段中有how can I make pork类似的提问，你就用英文回答其他语言一律给出英文回答，回答中只包含原料，用量和做法,不需要用sure之类的语言回应我的要求，NA代表适量")
                context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
                if 'none' or 'Error' not in food_keyword1:
                    save_to_redis(food_keyword, reply)
                else:
                    return
    else:
        reply_message = chatgpt.submit(update.message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def main():
    config = configparser.ConfigParser()
    config.read('./config.ini')
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
