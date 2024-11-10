from atproto import Client
from atproto import client_utils
import cv2
from argparse import ArgumentParser
import os
from pathlib import Path
import re

from bluebot.LoginConfig import LoginConfig, loadLoginConfig
from bluebot.ScheduleConfig import ScheduleConfig, ScheduleEntry, loadScheduleConfig
from bluebot import TimestampFile


def getClient(loginConf: LoginConfig) -> Client:
    client = Client()
    loginEntry = loginConf.getLogin('bluesky')
    client.login(loginEntry.username, loginEntry.password)
    return client


def readAndResizeImage(imagePath):
    image = cv2.imread(imagePath, 1)
    resizedImage = cv2.resize(image, (int(len(image[0]) / 2), int(len(image) / 2)), interpolation=cv2.INTER_LINEAR)

    # cv2.imwrite("temp.jpg", resizedImage)
    # with open("/tmp/temp.jpg", 'rb') as f:
    #     image = f.read()
    # os.remove("/tmp/temp.jpg")

    # default JPG quality
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
    # write to memory
    result, jpgImage = cv2.imencode('.jpg', resizedImage, encode_param)
    jpgImageBytes = jpgImage.tobytes()

    print("read image {}, {}x{} -> {}x{} ({} bytes)".format(imagePath, len(image[0]), len(image), len(resizedImage[0]), len(resizedImage), len(jpgImageBytes)))

    return jpgImageBytes


def sendPost(client: Client, entry: ScheduleEntry, dry = False) -> None:
    # adapted from https://github.com/MarshalX/atproto/blob/main/examples/send_images.py
    #          and https://atproto.blue/en/latest/atproto_client/utils/text_builder.html
    text = entry.text
    paths = entry.images
    image_alts = entry.alts

    images = [readAndResizeImage(path) for path in paths]

    textBuilder = client_utils.TextBuilder()
    index = 0
    while True:
        match = re.search("#([^ #]+)", text[index:])
        if match is None:
            break
        if match.span()[0] > index:
            print("Adding text: " + text[index:match.span()[0]])
            textBuilder.text(text[index:match.span()[0]])
        print("Adding tag: " + match.group(0))
        textBuilder.tag(match.group(0), match.group(1))
        index = match.span()[1]
    if index < len(text):
        print("Adding last text: " + text[index:len(text)])
        textBuilder.text(text[index:len(text)])

    print("Sending post:\n{}".format(entry))
    for image in images:
        print("Sending image ({} bytes)".format(len(image)))

    if dry:
        print("Dry Run")
    else:
        client.send_images(text=textBuilder, images=images, image_alts=image_alts)


def run(loginConf: LoginConfig, scheduleConf: ScheduleConfig, statePath, dry = False, verify = False, force = None) -> None:
    if force is not None:
        entriesToSend = scheduleConf.getEntry(force)
        if len(entriesToSend) == 0:
            raise(Exception("Entry {} not found".format(force)))
        currentTimestamp = None
    elif verify:
        entriesToSend = scheduleConf.getAllEntries()
        dry = True
        currentTimestamp = None
    else:
        lastTimestamp = TimestampFile.loadTimestamp(statePath)
        currentTimestamp = TimestampFile.currentTimeStamp()
        entriesToSend = scheduleConf.getEntriesBetween(lastTimestamp, currentTimestamp)

    if len(entriesToSend) == 0:
        print("Found no entries to send")
    else:
        if dry:
            client = None
        else:
            client = getClient(loginConf)

        for e in entriesToSend:
            sendPost(client, e, dry)

    if force is None and not dry:
        TimestampFile.saveTimestamp(statePath, currentTimestamp)


def main():
    parser = ArgumentParser(
        prog='bluebot',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-s', '--schedule', required=True)
    parser.add_argument('-l', '--login', required=True)
    parser.add_argument('-t', '--state', required=True)
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--force', required=False)

    args = parser.parse_args()

    loginConf = loadLoginConfig(args.login)
    scheduleConf = loadScheduleConfig(args.schedule)
    statePath = args.state
    dry = args.dry
    verify = args.verify
    force = args.force

    scheduleFile = Path(args.schedule)
    scheduleDir = scheduleFile.parent
    os.chdir(scheduleDir)

    run(loginConf, scheduleConf, statePath, dry, verify, force)
