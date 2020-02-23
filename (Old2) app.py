from __future__ import unicode_literals
import errno
import os
import sys
import tempfile
import json
from argparse import ArgumentParser

from flask import Flask, request, abort, escape, jsonify

import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

# line bot
channel_secret = 'e94b621bcd5791c77376ee4c12d8d102'
channel_access_token = 'L9XAALu+ycCiKGh+1oFf00ecQy7WlsIVJH4tuZPM7OmwDrZqXx58skJyOqy4G4mPKQ0ACBnZaFdbRsvaZdSAyIXZ37EEPoGabjkBBS4oouxIbnYacJz0WAzr8Fhc7kH2DevZLdPzf8x1PTqZdEKc+wdB04t89/1O/w1cDnyilFU='

user_id = 'Uad677bb930b40aed843edaa385eae45d'

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

app = Flask(__name__)

sentstatus = {
    "sentdata": "0",
    "valve": "0",
    "auto": "0"
}
sentstatus = json.dumps(sentstatus)  # convernt Python to JSON


# ^-^
@app.route('/')
def hello():
    return 'Hello my name is Tham / Nontacha'


@app.route('/notification', methods=['POST'])  # board sent
def add_message():
    content = request.get_json()  # get json and convert to python
    print(content)
    line_bot_api.push_message(user_id, TextSendMessage(
        text="-----Please water the plants!-----\n\nNow Soil moisture "+str(content['soil moisture']) + " %"))
    return "OK"


# from dialogflow that connect with line bot
@app.route('/requestdata', methods=['POST'])
def webhook():
    # get data from dialogflow
    content = request.get_json(silent=True, force=True)
    print(content)
    global sentstatus
    sentstatus = json.loads(sentstatus)  # Reading json file (JSON to Python)
    # Use try because use dialogflow to sent one data, can know by print(content)
    try:
        sentdata_flag = content["queryResult"]["outputContexts"][0]["parameters"]["sentdata"]
        if(sentdata_flag == "sentdat"):
            sentstatus["sentdata"] = 1
        print("sentdata : "+str(sentstatus["sentdata"]))

    except KeyError:
        try:
            valve_flag = content["queryResult"]["outputContexts"][0]["parameters"]["valve"]
            print(valve_flag)
            if(valve_flag == "OnValve" or valve_flag == "On"):
                sentstatus["valve"] = 1
            if(valve_flag == "OffValve" or valve_flag == "Off"):
                sentstatus["valve"] = 0
            print("value : "+str(sentstatus["valve"]))
        except KeyError:
            auto_flag = content["queryResult"]["outputContexts"][0]["parameters"]["auto"]
            if(auto_flag == "yes"):
                sentstatus["auto"] = 1
            if(auto_flag == "no"):
                sentstatus["auto"] = 0
            print("auto : "+str(sentstatus["auto"]))
    line_bot_api.push_message(
        user_id, TextSendMessage(text=". . .Working. . ."))
    sentstatus = json.dumps(sentstatus)  # convernt Python to JSON
    return "Dialogflow"


@app.route('/sensordatastatus')  # for Board get data
def status():
    return sentstatus


@app.route('/sensordatastatus', methods=['POST'])  # form board sent data
def changestatus():
    global sentstatus
    sentstatus = json.loads(sentstatus)  # Reading json file (JSON to Python)
    sentstatus["sentdata"] = 0
    print(sentstatus["sentdata"])
    sentstatus = json.dumps(sentstatus)  # convernt Python to JSON
    data = request.get_json()
    print(data)
    Text = ""
    Text += "****************************\n\n"
    Text += "Humidity         = "+str(data["humidity"])+" %\n"
    Text += "Temperature   = "+str(data["temp C"])+" °C\n"
    Text += "Soil Moisture  = "+str(data["soil moisture"])+" %\n"
    Text += "Valve                = "+str(data["valvestat"])+"\n"
    Text += "Auto                 = "+str(data["auto"])+"\n\n"
    Text += "****************************"
    print(Text)
    line_bot_api.push_message(
        user_id, TextSendMessage(text=Text))
    return "DONE"


@app.route('/automodereply', methods=['POST'])
def automodereply():
    reply = request.get_json()
    print(reply)
    line_bot_api.push_message(
        user_id, TextSendMessage(text=reply["automode"]))
    return "REPLY"


@app.route('/valvereply', methods=['POST'])
def valvereply():
    reply = request.get_json()
    print(reply)
    line_bot_api.push_message(
        user_id, TextSendMessage(text=reply["valve"]))
    return "REPLY"
