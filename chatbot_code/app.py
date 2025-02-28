from flask import Flask, request, jsonify, render_template
import os
import boto3
import json
import yfinance as yf
from yahooquery import search

inferenceProfileArn= os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")

app = Flask(__name__)

bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")

#### 주식 가격 관련 함수 ####
def get_stock_symbol(company_name):
    result = search(company_name)
    quotes = result.get("quotes", [])
    if quotes:
        return quotes[0]["symbol"]
    return None

def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    price = stock.history(period="5d")["Close"].iloc[-1]
    return round(price, 2)

def get_currency(symbol):
    if ".KQ" in symbol or ".KS" in symbol:
        return "원"
    return "달러"

company_list = ["Apple"]
def find_company(text):
    for company in company_list:
        if company in text:
            return company
    return ""
#### ------------------ ####

def chatbot_response(user_input):
    company_name = find_company(user_input)
    symbol = get_stock_symbol(company_name)

    stock_info = ""

    if symbol:
        stock_price = get_stock_price(symbol)
        currency = get_currency(symbol)
        stock_info = f"{company_name}의 주가는 {stock_price}{currency}입니다."

    prompt = (
        f"너는 AI 비서야. 질문에 대해 친절하고 유익한 답변을 해줘."
        f"주식 정보가 포함된 경우 가격을 포함해서 답변해줘."
        f"일반적인 질문이면 적절한 답변을 해줘."
        f"무조건 200자 이내에 답변을 해줘줘"
        f"질문: {user_input}\n"
        f"답변:"
    )

    response = bedrock_client.invoke_model(
        modelId=inferenceProfileArn,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }),
    )

    ai_response = json.loads(response["body"].read())["content"][0]["text"]

    return stock_info if stock_info else ai_response.strip()

#### Flask 엔드포인트 ####
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "메시지가 없습니다."}), 400

    user_input = data["message"].strip() 

    if not user_input:
        return jsonify({"error": "빈 메시지입니다."}), 400

    response = chatbot_response(user_input) 
    return jsonify({"response": response})
#### ---------------- ####

@app.route("/")
def index():
    return render_template("index.html") 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
