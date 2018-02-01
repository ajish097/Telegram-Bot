from flask import Flask
from flask import request,jsonify
import requests
from crypto_symbol import crypto_list
#include this if you want to host on http
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

url = 'https://api.telegram.org/bot'
token = '<token>'

def send_message(chat_id,text):
	URL = url+token+'sendMessage'
	answer = {'chat_id': chat_id, 'text': text}
	r = requests.post(URL,json = answer)

def make_pnr_dict(response):
    pnr = {}
    pnr['pnr'] = response['pnr']
    pnr['train-number'] = response['train']['number']
    pnr['train-class'] = response['train']['classes'][0]['code']
    pnr['train-name'] = response['train']['name']
    pnr['from'] = response['from_station']['name']
    pnr['To'] = response['reservation_upto']['name']
    pnr['status'] = response['passengers']
    return pnr 

@app.route('/<token>', methods = ['GET','POST'])
def index():
	if request.method == 'POST':
		r = request.get_json()
		chat_id = r['message']['chat']['id']
		received_text = r['message']['text'].split() #The received text must be in the form pnr status <pnr> or should contain legit crypto symbol.
		for word in received_text:
			if word.upper() in crypto_list:
				text = requests.get('https://min-api.cryptocompare.com/data/price?fsym='+str(word.upper())+'&tsyms=INR').json()['INR']
				send_message(chat_id,str(u"\u20B9")+" "+str(text))
				return'OK'
			elif 'pnr'.lower() == word.lower():
				try:
					response = requests.get("https://api.railwayapi.com/v2/pnr-status/pnr/"+received_text[2]+"/apikey/<toke>/").json()
					pnr = make_pnr_dict(response)
					send_message(chat_id,pnr)
					return'OK'
				except:
					send_message(chat_id,"Please try after some time")
					return'OK'
	
		msg = "The query you have requested is incorrect. Please include legit crypto symbol or include pnr status <pnr number> in your query for a valid response."
		send_message(chat_id, msg)
		return'OK'

	else:
		return "Bot is set"

	return'OK'

if __name__ == '__main__':
    app.run()