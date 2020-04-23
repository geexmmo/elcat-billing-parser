import json
import logging
from urllib import request, parse, error

billing_url_link="https://login.elcat.kg/cgi-bin/clients/deal_account?session_id="
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")

def Prepare_formatting(url, data):
    post_data = {
        "username": "Телефончик",
        "icon_emoji": ":telephone:",
        "text": "message",
        "attachments": [
            {
            "title": "login.elcat.kg",
            "title_link": "https://billingloginurl",
            "text": "Rocket.Chat, the best open source chat",
            }
            ]
        }

    out_message="Недостаток денежных средств на счету для оплаты следующего месяца, возможно отключение услуг телефонии: \n\n"
    out_message+="Внутренний идентификатор: " + data['account_internal_name'] + "\n"
    out_message+="Договор: " + data['account_id'] + " " + data['account_name'] + "\n"
    out_message+="Баланс: " + str(data['account_balance']) + " сом\n"
    numbers = str(data['account_services']).replace("'","").replace(']',"").replace("[","")
    out_message+="Зарегестрированные номера: " + numbers + "\n"
    out_message+="Текущий статус: " + data['account_status']

    post_data['text'] = out_message
    post_data['attachments'][0]['title_link'] = str(billing_url_link + data['sessid'])
    post_data['attachments'][0]['text'] = str("Проверка баланса для: " + data['account_id'])
    
    post_data = json.dumps(post_data)

    req = request.Request(url, post_data.encode('utf-8'))
    req.add_header("Content-Type","application/json")
    try: 
        with request.urlopen(req) as resp:
            resp.read()
    except error.URLError as e:
            logging.error("Rocket chat error: %s", e)

def RocketChat_send(url, data, usd_price):
    for i in data:
        if len(data[i]['account_services']) > 1:
            if data[i]['account_balance'] <= usd_price * 2:
                Prepare_formatting(url, data[i])
        else:
            if data[i]['account_balance'] <= usd_price:
                Prepare_formatting(url, data[i])