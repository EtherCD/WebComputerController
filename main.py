from flask import *
from sys import platform
import pyautogui as pg
import json
import os

level_of_controll = 3
mouse_speed = 10

def isLinuxOrWindows():
    if platform == "linux" or platform == "linux2":
        return True
    elif platform == "win32":
        return False

if isLinuxOrWindows():
    import alsaaudio
elif not isLinuxOrWindows():
    import pywinauto as pw
    from Sound import Sound

def getAllTranslates():
    return os.listdir("./translates")

#This is a translation for the output of Russian and other languages for Linux
#If necessary, you can replace the signs of your language in turn, the same letter is only in English
ru_translate = {'ь':'m', 'а':'f', 'б':',', 'в':'d',
       'г':'u', 'д':'l', 'е':'t', 'ё':'`', 'ж':';',
       'з':'p', 'и':'b', 'й':'q', 'к':'r', 'л':'k',
       'м':'v', 'н':'y', 'о':'j', 'п':'g', 'р':'h', 
       'с':'c', 'т':'n', 'у':'e', 'ф':'a', 'х':'[',
       'ц':'w', 'ч':'x', 'ш':'i', 'щ':'o', 'ы':'s',
       'э':"'", 'ю':'.', 'я':'z', 'з':'p'}

app = Flask(__name__)

translate = {}

@app.route("/", methods = ['POST', 'GET'])
def index():
    if request.method=='GET' and request.args.get("volume"):
        volume:int = request.args.get("volume")
        print("Getted request to change Volume: "+volume)
        setVolume(int(volume))
    elif request.method=='GET' and request.args.get("control"):
        if isLinuxOrWindows():
            pg.press(request.args.get("control"))
        elif not isLinuxOrWindows():
            if request.args.get("control") == "f":
                pg.press("f")
            else:
                pw.keyboard.send_keys(translateKeyToWinKey(request.args.get("control")))
    elif request.method=='GET' and request.args.get("text_to_put"):
        text=request.args.get("text_to_put")
        if isLinuxOrWindows():
            writeRaETextLinux(text, control0="win", control1="space")
        elif not isLinuxOrWindows():
            pw.keyboard.send_keys(request.args.get("text_to_put"))
    elif request.method=='GET' and request.args.get("mouse"):
        mouse = request.args.get("mouse")
        applyMouseMovement(mouse)
    return render_template("index.html", current_volume=getVolume(), level_of_controll=level_of_controll, mouse_speed=mouse_speed)


def setVolume(volume: int):
    if volume >= 0 and volume <= 100:
        if isLinuxOrWindows():
            m = alsaaudio.Mixer()
            m.setvolume(volume)
        elif not isLinuxOrWindows():
            Sound.volume_set(volume)
    
def getVolume():
    if isLinuxOrWindows():
        m=alsaaudio.Mixer()
        return m.getvolume()[0]
    else:
        return Sound.current_volume()
    return 0

def applyMouseMovement(mouse):
    if mouse=="up": pg.move(0, -mouse_speed)
    if mouse=="down": pg.move(0, mouse_speed)
    if mouse=="left": pg.move(-mouse_speed, 0)
    if mouse=="right": pg.move(mouse_speed, 0)
    if mouse=="click": pg.click()

def translate(translate, text):
    result=""
    len_text=len(text)
    for i in range(0,len_text):
        simb=""
        if text[i] in translate:
            simb = translate[text[i]]
        else:
            simb = text[i]
        result = result + simb
    return result

def writeRaETextLinux(text, control0="", control1="", interval=0.25):
    current_lang=os.system("xset -q | grep LED | awk '{print $10}' | cut -c 5")
    if bool(set(ru_translate).intersection(set(text.lower()))):
        if current_lang:
            pg.typewrite(text, interval=interval)
        else:
            if not control0:
                pg.hotkey("shift", "alt")
                pg.typewrite(translate(ru_translate, " "+text), interval=interval)
                pg.hotkey("shift", "alt")
            else:
                pg.hotkey(control0, control1)
                pg.typewrite(translate(ru_translate, " "+text), interval=interval)
                pg.hotkey(control0, control1)
    else:
        if current_lang:
            pg.write(text, interval=interval)
        else:
            if not control0:
                pg.hotkey("shift", "alt")
                pg.write(text, interval=interval)
                pg.hotkey("shift", "alt")
            else:
                pg.hotkey(control0, control1)
                pg.write(text, interval=interval)
                pg.hotkey(control0, control1)

def translateKeyToWinKey(key: str):
    if str == "up" or str == "down" or str == "left"or str == "right": 
        return "{VK_"+key.upper()+"}"
    return "{"+key.upper()+"}"

if __name__ == "__main__":
    if translate != {}:
        s = False
        if not os.path.isfile("./settings.json"):
            with open("settings.json", "r+") as f:
                if f.read() == "":
                    s=True
        if s:
            translates = getAllTranslates()
            print("Set Language:")
            for translate in translates:
                with open("./translates/"+translate, encoding="utf-8") as f:
                    translateF=json.load(f)
                    print(translate+":"+translateF["Name"])
            inp = input("Put Translate Name(en):")
            if inp+".json" in translates:
                with open("./translates/"+inp+".json", encoding="utf-8") as f:
                    translateF=json.load(f)
                    translate=translateF
                with open("settings.json", "w+") as f:
                    f.write('{"currentT":"'+inp+'"}')
                print("Setted!")
                app.run(debug=True, host='0.0.0.0')
            print("This not option")
        else:
            with open("settings.json", "r+") as f:
                ct = json.load(f)
            if ct["currentT"] != "":
                with open("./translates/"+ct["currentT"]+".json", encoding="utf-8") as f:
                    translateF=json.load(f)
                    translate=translateF
            app.run(debug=True, host='0.0.0.0')
    else:
        app.run(debug=True, host='0.0.0.0')
