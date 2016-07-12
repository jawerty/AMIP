import subprocess
import os
import re
import requests
import uuid
import smtplib
from smtplib import SMTPException

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask
from flask import render_template, request, redirect, url_for, send_from_directory
from readability.readability import Document
import urllib
 
cwd = os.getcwd()
app = Flask(__name__, static_url_path='/static/')

def sendAMIPEmail(receivers, subject, body, image_id):
    receivers = [x.strip() for x in receivers.split(',')]
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = "jawerty210@gmail.com"
    msg['To'] = receivers


    body = body + "<br><img src='http://162.243.74.219:5000/p/"+image_id+"'></img>"
    html = MIMEText(body, 'html')

    msg.attach(html)

    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()

        mail.starttls()

        console.log(os.environ["GPWD"])
        mail.login('"jawerty210@gmail.com"', os.environ["GPWD"])
        mail.sendmail("jawerty210@gmail.com", receivers, msg.as_string())
        mail.quit()

        return True
    except SMTPException as e:
        print e
        return False

def genScript(HTML):
    # HTML = HTML.replace('"', "'").replace("<html><body>", "").replace("</body></html>", "").replace("<script", "<span hidden").replace("</script>", "</span>").replace("src=", "data-src=").replace("href=", "data-href=")
    HTML = HTML.replace('"', "'")
    convertImgToDataUrl = ("function convertImgToDataUrl(elementId, callback) {"
        "window.imageConverting = false;"
        "var imgs = document.getElementById(elementId).getElementsByTagName('img');"
        "var returnUrls = [];"
        "if (imgs.length < 1) callback(true, null);"
        "for (var i = 0; i<imgs.length; i++) {"
            "var tempImage = new Image();"
            "tempImage.crossOrigin = 'Anonymous';"
            "tempImage.onload = function(){"
                "window.imageConverting = true;"
                "console.log('load');"
                "var canvas = document.createElement('CANVAS');"
                "var ctx = canvas.getContext('2d');"
                "canvas.height = this.height;"
                "canvas.width = this.width;"
                "ctx.drawImage(this, 0, 0);"
                "var dataURL = canvas.toDataURL('image/png');"
                "returnUrls.push(dataURL);"
                "canvas = null; "

                "if (i == imgs.length-1) {"
                    "console.log(returnUrls);"
                    "for (var x = 0; x<imgs.length; x++) {"
                        "imgs[x].src = returnUrls[x];"
                    "};"
                    "setTimeout(function(){"
                        "callback(false, document.getElementById('elementId'));"
                    "}, 1000);"
                "};"
            "};"
            "tempImage.src = imgs[i].src;"
            "if (i == imgs.length-1 && !window.imageConverting) {"
                "setTimeout(function(){"
                    "callback(true, null);"
                "}, 100);"
            "};"
        "};"
    "};")
    htmlToCanvas = ( "function htmlToCanvas(cb) {"
        "var canvas = document.getElementById(\"CANVAS\");"
        "var div = document.createElement('div');"
        "div.setAttribute('id', 'temp_article');"
        "div.innerHTML = \"%s\";"
        "document.getElementById('CONTENT').appendChild(div);"

        "var temp_article = document.getElementById('temp_article');"
        "var height = temp_article.clientHeight;"
        "var width = temp_article.clientWidth;"
        "canvas.height=height;canvas.width=width;"
        "var parent_ctx = canvas.getContext('2d');"

        "convertImgToDataUrl('temp_article', function(err, temp_article_final){"
            "if (err) {"
                "console.log(err);"
                "temp_article_final = temp_article;"
            "}"
            "var xhtml = new XMLSerializer().serializeToString(temp_article_final);"

            "var data = '<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"'+width+'\" height=\"'+height+'\" ><foreignObject externalResourcesRequired=\"true\" width=\"100%%\" height=\"100%%\"><body xmlns=\"http://www.w3.org/1999/xhtml\" style=\"font-size:15px\">'+xhtml+'</body></foreignObject></svg>';"
            "var encodedData = data;"
            "var DOMURL = window.URL || window.webkitURL || window;"

            "var img = new Image(width, height);"
            "var svg = new Blob([data], {type: 'image/svg+xml;charset=utf-8'});"
            "var url = DOMURL.createObjectURL(svg);"
            "console.log(data, img, svg, url);"
            "img.onload = function () {"
                "parent_ctx.drawImage(img, 0, 0);"
                "DOMURL.revokeObjectURL(url);"
                "setTimeout(function() {"
                    "cb();"
                "}, 1000);"
            "};"

            "img.src = url;"
        "});"
        "};"
    )  % HTML

    script = convertImgToDataUrl+htmlToCanvas
    print script
    return script

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/maip", methods=["POST"])
def maip():
    display = Display(visible=0, size=(1024, 768))

    article_link = request.form.get('article_link')
    isNYT = request.form.get('nyt', False)

    if isNYT:
        logo = "<svg id='NYT-LOGO' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 10 14.266' style='enable-background:new 0 0 10 14.266;' xml:space='preserve'><g id='trace' style='display:none;'></g><g id='Layer_1'><g><g><g><path d='M8.14,0.14c0.367,0.027,0.946,0.212,1.382,0.592c0.461,0.45,0.569,1.133,0.406,1.752c-0.146,0.552-0.307,0.839-0.872,1.22C8.489,4.092,7.801,4.059,7.801,4.059v2.39l1.165,0.942L7.801,8.333v3.261c0,0,1.166-0.672,1.89-2.165c0,0,0.03-0.084,0.097-0.241c0.065,0.404,0.028,1.217-0.427,2.257c-0.342,0.784-0.962,1.542-1.743,1.975c-1.383,0.764-2.421,0.839-3.53,0.608c-1.3-0.271-2.483-0.999-3.293-2.274c-0.563-0.897-0.817-1.942-0.794-3.07C0.048,6.48,1.686,4.579,3.583,3.866c0.232-0.084,0.322-0.143,0.649-0.171C4.082,3.797,3.909,3.928,3.694,4.07C3.083,4.474,2.558,5.271,2.337,5.885l3.677-1.639v5.142l-2.963,1.481c0.338,0.476,1.364,1.182,2.244,1.28c1.491,0.167,2.369-0.485,2.369-0.485L7.662,8.333L6.505,7.391l1.159-0.939V4.059c-0.631-0.074-1.4-0.283-1.847-0.395C5.156,3.501,2.956,2.885,2.611,2.833C2.265,2.784,1.841,2.799,1.582,3.028C1.324,3.262,1.164,3.672,1.274,4.039c0.061,0.21,0.205,0.331,0.314,0.449c0,0-0.127-0.01-0.358-0.146c-0.414-0.25-0.73-0.74-0.768-1.342C0.416,2.217,0.739,1.505,1.387,1.026C1.952,0.664,2.59,0.433,3.333,0.537c1.083,0.154,2.539,0.768,3.835,1.081c0.503,0.121,0.892,0.16,1.245-0.045c0.167-0.116,0.455-0.421,0.219-0.833C8.358,0.264,7.827,0.278,7.379,0.19C7.763,0.111,7.851,0.111,8.14,0.14z M3.767,10.36V5.394L2.271,6.064c0,0-0.38,0.85-0.313,2.087C2.01,9.12,2.55,10.276,2.966,10.76L3.767,10.36z'/></g></g></g></g><g id='Layer_3' style='display:none;'></g></svg>"
    else:
        logo = ""

    print "Converting article "+article_link+"..."

    r = requests.get(article_link, headers={"Connection":"close", "User-Agent" : "AMIP"})
    
    html = r.text
    style = """
        <style>
            @font-face {
              font-family: cheltenham;
              src: url('https://a1.nyt.com/fonts/family/cheltenham/cheltenham-normal-800.ttf');
              font-style: normal;
              font-weight: 800;
            }
            @font-face {
              font-family: franklin;
              src: url('https://a1.nyt.com/fonts/family/franklin/franklin-normal-500.ttf');
              font-style: italic;
              font-weight: 300;
            }


            #BODY {
                color: #333;
                font-family: franklin;
            }

            #NYT-LOGO {
                height: 54px;
                width: 28;
                display: inline;
            }
            
            #TITLE {
                color: #000;
                font-family: cheltenham;
                font-size: 36px;
                border-bottom: 1px solid #ccc;
            }

            #TITLE-LABEL {
                float: right;
                display: block;
                font-size: 12px;
                color: #777;
            }

            #BIG_CONTENT {
                max-width: 650px;
            }
        </style>
    """

    document = Document(html)
    readable_article = "<div id='BODY'>"+document.summary()+"</div>"
    readable_title = "<p id='TITLE-LABEL'>*generated with AMIP</p><h1 id='TITLE'>"+logo+document.short_title()+"</h1>"
    readable_author = "<hr><p>By AUTHOR</p><hr>"
    formatted_article = style+"<div id='BIG_CONTENT'>"+readable_title+readable_article+"</div>"
    display.start()
    fp = webdriver.FirefoxProfile()

    # fp.set_preference("permissions.default.image",1)
    fp.set_preference('webdriver.log.file', '/tmp/firefox_console')
    fp.set_preference("gfx.downloadable_fonts.enabled",True)
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", cwd+"/static/")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

    driver = webdriver.Firefox(firefox_profile=fp)
    
    driver.get("file://"+cwd+"/driver.html")

    # soup = BeautifulSoup(formatted_article, 'html.parser')
    soup = BeautifulSoup(formatted_article, "lxml")
    formatted_article = soup.prettify()
    new_formatted_article = str.join(" ", formatted_article.splitlines())

    ID = str(uuid.uuid4().get_hex().upper()[0:6])
    htmlToCanvas = genScript(new_formatted_article)

    renderDefaultImages = ("var tempImage = new Image();"
                    "tempImage.crossOrigin = 'Anonymous';"
                    "tempImage.onload = function(){"
                        "var canvas = document.createElement('CANVAS');"
                        "var ctx = canvas.getContext('2d');"
                        "canvas.height = this.height;"
                        "canvas.width = this.width;"
                        "ctx.drawImage(this, 0, 0);"
                        "var dataURL = canvas.toDataURL('image/svg');"
                        "console.log('DATAU:', dataURL);"
                        "document.getElementById('NYT-LOGO').setAttribute('src',dataURL);"
                    "};"
                    "tempImage.src = 'file:///var/www/AMIP/static/images/icon-t.svg';")

    download_script = ("htmlToCanvas(function(){"
                    "console.log('callback run');"
                    "var url = document.getElementById('CANVAS').toDataURL('image/png').replace(/^data:image\/[^;]/, 'data:application/octet-stream;filename="+ID+".png;');"
                    "var trigger = document.getElementById('download_trigger');"
                    "trigger.setAttribute('download', \""+ID+".png\");"
                    "trigger.setAttribute('href', url);"
                    "trigger.click();"
                        "setTimeout(function(){"
                            "var finished = document.createElement('span');"
                            "finished.setAttribute('id', 'finished');"
                            "document.getElementById('CONTENT').appendChild(finished);"
                        "}, 1000);"
                    "});")

    driver.execute_script(htmlToCanvas+download_script)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "finished")), "Download PNG")

    print driver.get_log('browser')
    driver.quit()
    display.stop()

    # subprocess.call("mv "+ID+".png static/"+ID+".png", shell=True)
    return redirect(url_for("renderPic", picture_id=ID))

@app.route('/p/<picture_id>', methods=["GET"])
def renderPic(picture_id):
    return send_from_directory("static", picture_id+".png")

@app.route('/email', methods=["PUT"])
def email():
    receivers = request.form["receivers"]
    subject = request.form["subject"]
    body = request.form["body"]
    image_id = request.form["image_id"]

    email_sent = sendAMIPEmail(receivers, subject, body, image_id)

    if email_sent:
        return "Email sent"
    else:
        return "Email not sent"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
