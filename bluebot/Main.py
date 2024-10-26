from atproto import Client
import cv2
from argparse import ArgumentParser
import os

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
    image2 = cv2.resize(image, (int(len(image[0]) / 2), int(len(image) / 2)), interpolation=cv2.INTER_LINEAR)
    print("read image {}, {}x{} -> {}x{}".format(imagePath, len(image[0]), len(image), len(image2[0]), len(image2)))
    cv2.imwrite("temp.jpg", image2)

    with open("/tmp/temp.jpg", 'rb') as f:
        image = f.read()

    os.remove("/tmp/temp.jpg")
    return image


def sendPost(client: Client, entry: ScheduleEntry) -> None:
    # adapted from https://github.com/MarshalX/atproto/blob/main/examples/send_images.py
    text = entry.text
    paths = entry.images
    image_alts = entry.alts

    images = [readAndResizeImage(path) for path in paths]

    client.send_images(text=text, images=images, image_alts=image_alts)


def run(loginConf: LoginConfig, scheduleConf: ScheduleConfig, statePath, dry = False) -> None:
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
            if dry:
                print("Dry Run: Sending post:\n{}".format(e))
            else:
                print("Sending post:\n{}".format(e))
                # sendPost(client, e)

    if not dry:
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

    args = parser.parse_args()

    loginConf = loadLoginConfig(args.login)
    scheduleConf = loadScheduleConfig(args.schedule)
    statePath = args.state
    dry = args.dry

    run(loginConf, scheduleConf, statePath, dry)
