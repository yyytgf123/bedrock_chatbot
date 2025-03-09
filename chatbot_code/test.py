from flask import Flask, request, jsonify, render_template
import os
import boto3
import json
import yfinance as yf
from yahooquery import search
from company_dict import company_dict
# from googletrans import Translator
from deep_translator import GoogleTranslator


def translate_to_english(translate):
    return GoogleTranslator(source='ko', target='en').translate(translate)

def find_company_symbol(name):
    if not name.isascii(): # 한국어 아닌 경우
        name = translate_to_english(name)

    result = search(name)
    if result and 'quotes' in result and result["quotes"]:
        return result['quotes'][0]['symbol']
    return None

print(find_company_symbol("애플"))