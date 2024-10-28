# bluebot: Basic Ass BlueSky Scheduling Tool

## Linux Setup:
```
sudo apt-get update
sudo apt-get install python3-venv
sudo apt-get install ffmpeg libsm6 libxext6
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

## My Windows 11 IDE setup:
```
New-Item -ItemType SymbolicLink -Path "C:\<windows work directory>" -Target "\\wsl.localhost\Ubuntu\<linux work directory>"
```

## Usage:
```
python3 -m bluebot --schedule <schedule.conf> --login <login.conf> --state <time.txt> [--dry | --verify]
```

### Examples
Verifying a schedule conf:
```
python3 -m bluebot -l ~/.bluebot/login.conf -s ~/bluebot/2024-11/schedule.conf -t ~/.bluebot/timestamp.txt --verify
```

## Environment
I set everything up in my Linux environment under `~/.bluebot`:
```
ls -l ~/.bluebut
-rw------- 1 buff00n buff00n   68 Oct 28 19:09 login.conf
drwxrwxr-x 2 buff00n buff00n 4096 Oct 28 19:05 logs
-rwxrwxr-x 1 buff00n buff00n  348 Oct 28 19:14 run.sh
lrwxrwxrwx 1 buff00n buff00n   50 Oct 28 18:41 schedule -> /home/buff00n/....
-rw-rw-r-- 1 buff00n buff00n   19 Oct 28 19:17 timestamp.txt
```
 * `login.conf` contains my account information.  The format of this file is given below.
Make sure this file has `0600` permissions.
 * `logs` is a directory that `run.sh` can log to
 * `run.sh` is in this repo under `util`
 * `schedule` is a soft link to a directory that holds a `schedule.conf` file and all the images I want to send
   * `schedule/schedule.conf`: the format of the schedule file is given below
 * `timestamp.txt`: created automatically by `run.sh`, this stores the last time the bot was run

I set up a cron job to run once an hour, logging to a new file per week, and cleaning up logs older than 30 days:
```
0 * * * *       ~/.bluebot/run.sh
```

## File Formats

### login config
Example:
```
[bluesky]
username=<blue sky account>
password=<password>
```

### schedule config:
Example:
```
[1]
timestamp=2024-11-01 12:00:00
text=Here is a test message
image.1=test-image-1.png
alt.1=it's an image

[2]
timestamp=2024-11-01 12:00:00
text=Here is a test message
image.1=test-image-1.png
alt.1=it's an image
image.2=test-image-2.png
alt.2=it's another image
image.3=test-image-3.png
alt.3=it's a third image
image.4=test-image-4.png
alt.4=up to four images are supported
```
 * The `[..]` lines separate individual posts.  The actual contents in between the brackets doesn't matter as long as it's unique.
   * A lot of formats are supported, but I recommend sticking with `YYYY-MM-DD HH:MM:SS`
 * `timestamp`: The timestamp for the post.  As soon as this time passes, bluebot will send the post the next time it's run.
 * `text`: The text of the post
 * `image.1`: The path to the first image file.  If this is a relative path then it's relative to the directory containing the config file.
 * `alt.1`: The alt text for the first image
 * `image.2`, `image.3`, `image.4`: Second, third, and fourth images, if provided
 * `alt.2`, `alt.3`, `alt.4`: Alt text for the second, third, and fourth images, if provided

## TODO
 * Code comments
 * Timezone support
 * Multi-line text support