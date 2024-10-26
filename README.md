# bluebot: Basic Ass BlueSky Scheduling Tool

## Linux Setup:
```
sudo apt-get update
sudo apt-get install python3.10-venv
sudo apt-get install ffmpeg libsm6 libxext6
python3 -m venv venv
. ./venv/bin/activate
```

## My Windows 11 IDE setup:
```
New-Item -ItemType SymbolicLink -Path "C:\<windows work directory>" -Target "\\wsl.localhost\Ubuntu\<linux work directory>"
```

## Usage:

```
python3 -m bluebot --schedule <schedule.conf> --login <login.conf> --state <time.txt> [--dry]
```