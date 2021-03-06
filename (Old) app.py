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

channel_secret = '<Your line channel secret>'
channel_access_token = '<Your line channel access token>'


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

app = Flask(__name__)

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
    content3 = json.loads(content2)  # Reading json file (JSON to Python)
    line_bot_api.push_message('<Your user id>', TextSendMessage(text="-----Please water the plants!-----\n\nNow Soil moisture "+str(content3['soil moisture']) + " %"))
    return "OK"


@app.route('/requestdata', methods=['POST'])
def webhook():
    content = request.get_json(silent=True, force=True)
    print(content)
    global sentstatus
    sentstatus = json.loads(sentstatus)
    try:
        valve_flag = content["queryResult"]["outputContexts"][0]["parameters"]["valve"]
        print(valve_flag)
        if(valve_flag == "OnValve"):
            sentstatus["valve"] = 1
            line_bot_api.push_message('<Your user id>', TextSendMessage(text="Valve is ON"))

        if(valve_flag == "OffValve"):
            sentstatus["valve"] = 0
            line_bot_api.push_message('<Your user id>', TextSendMessage(text="Valve is OFF"))
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
    line_bot_api.push_message('<Your user id>', TextSendMessage(text=Text))
    return "DONE"
