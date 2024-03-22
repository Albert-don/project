import logging
import redis
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from ChatGPT_HKBU import HKBU_ChatGPT
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import configparser
# Global variable for Redis connection
global redis1
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_key_phrases(text):
    doc = nlp(text)
    # 提取名词短语
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    return noun_phrases
user_message = "how can i make a vanilla cake"
keywords = extract_key_phrases(user_message)
print(keywords)