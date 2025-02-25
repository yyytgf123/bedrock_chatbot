import boto3
import json
import yfinance as yf

bedrock_client = boto3.client("bedrock-runtime", region_name = "ap-northeast-2")

stock_symbols = {
    "삼성전자": "005930.KS",
    "애플": "AAPL",
    "구글": "GOOGL",
    "테슬라": "TSLA",
    "마이크로소프트": "MSFT",
    "아마존": "AMZN",
}

def get_stock_price(symbol):
    stock = yf.Ticker(symbol) # 특정 주식 데이터 가져옴
    price = stock.history(period="1d")["Close"].iloc[-1] # 과거 가격 정보를 가져옴
    return round(price, 2)

def chatbot_query(user_input):
    symbol = None
    for company, stock_symbol in stock_symbols.items():
        if company in user_input:
            symbol = stock_symbol
            break

    if symbol is None:
        return "알 수 없는 주식 종목입니다 다시 입력해주세요."
    
    stock_price = get_stock_price(symbol)

    prompt = f"현재 {symbol} 주가는 {stock_price}달러 입니다. 시장 분석을 요약해줘."

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

user_input = "테슬라 주가 알려줘"
response = chatbot_query(user_input)
print(response)