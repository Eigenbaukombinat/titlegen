#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time

import logging
logging.basicConfig(level=logging.INFO)

sys.path.append('../')
from obswebsocket import obsws, events  # noqa: E402

host = "ratte"
port = 4444
password = ""


def on_event(message):
    print(u"Got message: {}".format(message))


def on_switch(message):
    print(u"You changed the scene to {}".format(message.getSceneName()))


ws = obsws(host, port, password)
ws.register(on_event)
ws.register(on_switch, events.SwitchScenes)
ws.connect()
