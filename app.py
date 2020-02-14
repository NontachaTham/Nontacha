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

channel_secret = 'e94b621bcd5791c77376ee4c12d8d102'
channel_access_token = 'L9XAALu+ycCiKGh+1oFf00ecQy7WlsIVJH4tuZPM7OmwDrZqXx58skJyOqy4G4mPKQ0ACBnZaFdbRsvaZdSAyIXZ37EEPoGabjkBBS4oouxIbnYacJz0WAzr8Fhc7kH2DevZLdPzf8x1PTqZdEKc+wdB04t89/1O/w1cDnyilFU='


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

app = Flask(__name__)

# line_bot_api.broadcast(TextSendMessage("Hello"))
sentstatus = {
    "sentdata": "NONE",
    "valve": "NONE",
}
sentstatus = json.dumps(sentstatus)


@app.route('/')
def hello():
    return 'Hello Tham'


@app.route('/notification', methods=['POST'])
def add_message():
    content = request.get_json()
    print(content)
    content2 = json.dumps(content)  # convernt Python to JSON
    # sentence = "data"+content2
    # line_bot_api.broadcast(TextSendMessage(sentence))
    content3 = json.loads(content2)  # Reading json file (JSON to Python)
    # line_bot_api.broadcast(TextSendMessage(Text))
    line_bot_api.push_message('Uad677bb930b40aed843edaa385eae45d', TextSendMessage(text="-----Please water the plants!-----\n\nNow Soil moisture "+str(content3['soil moisture']) + " %"))
    return "OK"


@app.route('/requestdata', methods=['POST'])
def webhook():
    content = request.get_json(silent=True, force=True)
    print(content)
    # queryResult.outputContexts.parameters.valve
    global sentstatus
    sentstatus = json.loads(sentstatus)
    try:
        valve_flag = content["queryResult"]["outputContexts"][0]["parameters"]["valve"]
        print(valve_flag)
        if(valve_flag == "OnValve"):
            sentstatus["valve"] = 1
            line_bot_api.push_message('Uad677bb930b40aed843edaa385eae45d', TextSendMessage(text="Valve is ON"))

        if(valve_flag == "OffValve"):
            sentstatus["valve"] = 0
            line_bot_api.push_message('Uad677bb930b40aed843edaa385eae45d', TextSendMessage(text="Valve is OFF"))
        print("value : "+str(sentstatus["valve"]))
    except KeyError:
        sentdata_flag = content["queryResult"]["outputContexts"][0]["parameters"]["sentdata"]
        if(sentdata_flag == "sentdat"):
            sentstatus["sentdata"] = 1
        print("sentdata : "+str(sentstatus["sentdata"]))
    sentstatus = json.dumps(sentstatus)
    return "None"


@app.route('/sensordatastatus')
def status():
    return sentstatus


@app.route('/sensordatastatus', methods=['POST'])
def changestatus():
    global sentstatus
    sentstatus = json.loads(sentstatus)
    sentstatus["sentdata"] = 0
    print(sentstatus["sentdata"])
    sentstatus = json.dumps(sentstatus)
    data = request.get_json()
    print(data)
    Text = ""
    Text += "****************************\n\n"
    Text += "Humidity         = "+str(data["humidity"])+" %\n"
    Text += "Temperature   = "+str(data["temp C"])+" °C\n"
    Text += "Soil Moisture  = "+str(data["soil moisture"])+" %\n"
    Text += "Valve                = "+str(data["valvestat"])+"\n\n"
    Text += "****************************"
    print(Text)
    line_bot_api.push_message('Uad677bb930b40aed843edaa385eae45d', TextSendMessage(text=Text))
    # flexmessage = json.dumps({
    # "type": "flex",
    # "altText": "Flex Message",
    # "contents": {
    #   "type": "bubble",
    #   "direction": "ltr",
    #   "header": {
    #     "type": "box",
    #     "layout": "baseline",
    #     "contents": [
    #       {
    #         "type": "text",
    #         "text": "Data",
    #         "size": "xl",
    #         "align": "start",
    #         "weight": "bold",
    #         "color": "#0D63BC"
    #       }
    #     ]
    #   },
    #   "body": {
    #     "type": "box",
    #     "layout": "vertical",
    #     "spacing": "none",
    #     "contents": [
    #       {
    #         "type": "separator",
    #         "color": "#999EA2"
    #       },
    #       {
    #         "type": "box",
    #         "layout": "baseline",
    #         "spacing": "none",
    #         "margin": "xs",
    #         "contents": [
    #           {
    #             "type": "text",
    #             "text": "Tempurature",
    #             "flex": 0,
    #             "margin": "none",
    #             "align": "start",
    #             "wrap": True
    #           },
    #           {
    #             "type": "text",
    #             "text": "53 C",
    #             "flex": 8,
    #             "margin": "none",
    #             "align": "end",
    #             "wrap": False
    #           }
    #         ]
    #       },
    #       {
    #         "type": "box",
    #         "layout": "baseline",
    #         "spacing": "none",
    #         "margin": "xs",
    #         "contents": [
    #           {
    #             "type": "text",
    #             "text": "Humidity",
    #             "flex": 0,
    #             "margin": "none",
    #             "align": "start",
    #             "wrap": True
    #           },
    #           {
    #             "type": "text",
    #             "text": "60 %",
    #             "flex": 8,
    #             "margin": "none",
    #             "align": "end",
    #             "wrap": False
    #           }
    #         ]
    #       },
    #       {
    #         "type": "box",
    #         "layout": "baseline",
    #         "spacing": "none",
    #         "margin": "xs",
    #         "contents": [
    #           {
    #             "type": "text",
    #             "text": "Soil moisture",
    #             "flex": 0,
    #             "margin": "none",
    #             "align": "start",
    #             "wrap": True
    #           },
    #           {
    #             "type": "text",
    #             "text": "70 %",
    #             "flex": 8,
    #             "margin": "none",
    #             "align": "end",
    #             "wrap": False
    #           }
    #         ]
    #       },
    #       {
    #         "type": "box",
    #         "layout": "baseline",
    #         "spacing": "none",
    #         "margin": "xs",
    #         "contents": [
    #           {
    #             "type": "text",
    #             "text": "Valve status",
    #             "flex": 0,
    #             "margin": "none",
    #             "align": "start",
    #             "wrap": True
    #           },
    #           {
    #             "type": "text",
    #             "text": "ON",
    #             "flex": 8,
    #             "margin": "none",
    #             "align": "end",
    #             "wrap": False
    #           }
    #         ]
    #       }
    #     ]
    #   },
    #   "footer": {
    #     "type": "box",
    #     "layout": "horizontal",
    #     "contents": [
    #       {
    #         "type": "button",
    #         "action": {
    #           "type": "message",
    #           "label": "Open valve",
    #           "text": "OnVlave"
    #         },
    #         "flex": 0,
    #         "style": "link"
    #       },
    #       {
    #         "type": "button",
    #         "action": {
    #           "type": "message",
    #           "label": "Close valve",
    #           "text": "OffValve"
    #         },
    #         "flex": 0,
    #         "style": "link"
    #       }
    #     ]
    #   },
    #   "styles": {
    #     "body": {
    #       "separator": False
    #     }
    #   }
    # }
    # }
    # )
    #line_bot_api.push_message('Uad677bb930b40aed843edaa385eae45d', TextSendMessage(text=Text))
    #line_bot_api.push_message('Uad677bb930b40aed843edaa385eae45d', FlexSendMessage(alt_text="hello", contents=json.loads(flexmessage)))
    return "DONE"
