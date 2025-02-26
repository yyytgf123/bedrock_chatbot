import boto3
import json
import yfinance as yf
from yahooquery import search

bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")

#### 주식 가격 출력 ####
def get_stock_symbol(company_name):
    result = search(company_name)
    quotes = result.get("quotes", [])

    if quotes:
        return quotes[0]["symbol"]
    return None

def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    price = stock.history(period = "5d")["Close"].iloc[-1]
    return round(price, 2)

def get_currency(symbol): # 국장이면 "원", 미장이면 "달러"
    if ".KQ" in symbol or ".KS" in symbol: 
        return "원"
    return "달러"

company_list = ["삼성전자", "애플","Apple"]
def find_company(text):
    for company in company_list:
        if company in text:
            return company
    return None
#### ---------------- ####

def chatbot_query(user_input):
    ### 회사명 찾기 ###
    words = user_input.split()
    company_name = find_company(words)

    symbol = get_stock_symbol(company_name)
    ### ----------- ###
        
    if symbol is None:
        return "해당 회사의 주식 정보를 찾을 수 없습니다. 정확한 이름을 입력해주세요."

    stock_price = get_stock_price(symbol)
    currency = get_currency(symbol)

    prompt = (
        f"(참고용) 1. 주식 정보 출력, 2. 200자 이내 답변, 3. 질문에 대한 사항 무조건 답변"
        f"만약 {stock_price}로 값을 받아온 질문이면 가격도 출력해줘"
        f"{user_input}에 따라 알맞는 답을 해줘."
    )


    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
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
                    "content": [
                        {
                            "type": "text",
                            "text": prompt 
                        }
                    ]
                }
            ]
        }),
    )

    ai_response = json.loads(response["body"].read())
    return ai_response["content"][0]["text"]

user_input = input()
response = chatbot_query(user_input)
print(response)
