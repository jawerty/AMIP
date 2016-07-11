# AMIP
## Run Instructions
```
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python server.py
```

## Build
Setup DO Server: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps

```
$ sudo apt-get update
$ sudo apt-get install firefox
$ sudo apt-get install xvfb
$ Xvfb :99 -screen 0 640x480x8 -nolisten tcp &
$ export DISPLAY=:99 # xvfb framebuffer settings
$ sudo apt-get build-dep python-lxml
$ sudo pip install -U selenium
$ sudo pip install pyvirtualdisplay

# Run Instructions
```

## TODO
- Saved images to local and use local urls in html
- Figure out svg foreign object styling
