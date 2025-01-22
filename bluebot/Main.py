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
from bluebot import client_more_utils


def getClient(loginConf: LoginConfig) -> Client:
    # todo: is there some other method that doesn't require storing/passing the password in plain text?
    # create a new client
    client = Client()
    # get the login for bluesky from the config
    loginEntry = loginConf.getLogin('bluesky')
    # login
    client.login(loginEntry.username, loginEntry.password)
    return client


def readAndResizeImage(imagePath):
    # read the image file
    image = cv2.imread(imagePath, 1)
    # resize by 50%
    # todo: make this configurable?
    width = int(len(image[0]) / 2)
    height = int(len(image) / 2)
    resizedImage = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    # default JPG quality
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
    # write to memory
    result, jpgImage = cv2.imencode('.jpg', resizedImage, encode_param)
    jpgImageBytes = jpgImage.tobytes()

    # logging
    print("read image {}, {}x{} -> {}x{} ({} bytes)".format(imagePath, len(image[0]), len(image), len(resizedImage[0]), len(resizedImage), len(jpgImageBytes)))

    # return the image file bytes
    return jpgImageBytes, height, width


def sendPost(client: Client, entry: ScheduleEntry, dry = False) -> None:
    # adapted from https://github.com/MarshalX/atproto/blob/main/examples/send_images.py
    #          and https://atproto.blue/en/latest/atproto_client/utils/text_builder.html
    # pull out the entry values
    text = entry.text
    paths = entry.images
    image_alts = entry.alts

    # read images and resize by 50%
    image_info = [readAndResizeImage(path) for path in paths]

    # start a text builder
    textBuilder = client_utils.TextBuilder()
    # initialize a starting index
    index = 0
    while True:
        # search the text for #tags or https://urls, starting at the last index
        # the only way I can find to search after a certain index is to slice the text, so
        # the resulting matcher's indexes will need to be offset by the start index.
        match = re.search("#([^ #]+)|https?://[^ ]+", text[index:])
        # no match found
        if match is None:
            break
        # if there's some plain text between matches then add it to the builder
        if match.span()[0] > 0:
            print("Adding text: " + text[index:index + match.span()[0]])
            # have to offset the matcher's span by the start index
            textBuilder.text(text[index:index + match.span()[0]])

        # if the match was a tag, add a tag element
        if match.group(0).startswith("#"):
            print("Adding tag: " + match.group(0))
            textBuilder.tag(match.group(0), match.group(1))
        # if the match was a URL, add a URL element
        elif match.group(0).startswith("http"):
            print("Adding url: " + match.group(0))
            textBuilder.link(match.group(0), match.group(0))

        # increment the index for the next search
        index = index + match.span()[1]

    # if there's some trailing plain text after the last match, add it to the builder
    if index < len(text):
        print("Adding last text: " + text[index:len(text)])
        textBuilder.text(text[index:len(text)])

    # logging
    print("Sending post:\n{}".format(entry))
    for (image, height, width) in image_info:
        print("Sending {}x{} image ({} bytes)".format(width, height, len(image)))

    if dry:
        # Dry run, don't send anything
        print("Dry Run")
    else:
        # call the client API with the text builder, images, alts, and dimensions
        # provided method doesn't support dimensions
        #client.send_images(text=textBuilder, images=images, image_alts=image_alts)
        images = [e[0] for e in image_info]
        image_dims = [(e[1], e[2]) for e in image_info]
        client_more_utils.send_images_with_dimensions(client=client, text=textBuilder, images=images, image_alts=image_alts, image_dims=image_dims)


def run(loginConf: LoginConfig, scheduleConf: ScheduleConfig, statePath, dry = False, verify = False, force = None) -> None:
    # get the list of entries to send in one of three ways
    if force is not None:
        # if --force is specified, get the entry from the schedule with that name
        entriesToSend = scheduleConf.getEntry(force)
        # sanity check
        if len(entriesToSend) == 0:
            raise(Exception("Entry {} not found".format(force)))
        # initialize this to make code analysis happy
        currentTimestamp = None
    elif verify:
        # if --verify is specified, then process all the entries in dry mode
        entriesToSend = scheduleConf.getAllEntries()
        dry = True
        # initialize this to make code analysis happy
        currentTimestamp = None
    else:
        # regular operation: get the last timestamp from the timestamp file
        lastTimestamp = TimestampFile.loadTimestamp(statePath)
        # current timestamp for comparison
        currentTimestamp = TimestampFile.currentTimeStamp()
        # get the schedule entries between the last and current timestamps
        entriesToSend = scheduleConf.getEntriesBetween(lastTimestamp, currentTimestamp)

    if len(entriesToSend) == 0:
        # log
        print("Found no entries to send")
    else:
        # only initialize the client if we're not in dry mode
        if dry:
            client = None
        else:
            client = getClient(loginConf)

        # send each entry
        for e in entriesToSend:
            sendPost(client, e, dry)

    # if w're not in --force mode or --dry mode, save the current timestamp for the next run
    if force is None and not dry:
        TimestampFile.saveTimestamp(statePath, currentTimestamp)


def main():
    # build the argument parser
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

    # parse the arguments
    args = parser.parse_args()

    # pull out parameters and flags
    loginConf = loadLoginConfig(args.login)
    scheduleConf = loadScheduleConfig(args.schedule)
    statePath = args.state
    dry = args.dry
    verify = args.verify
    force = args.force

    # read the schedule file
    scheduleFile = Path(args.schedule)
    # change the current working directory to the parent directory of the schedule file
    # this is so the schedule file can reference images files by relative path
    scheduleDir = scheduleFile.parent
    os.chdir(scheduleDir)

    # run the bot
    run(loginConf, scheduleConf, statePath, dry, verify, force)
