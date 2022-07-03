from flask import *
from sys import platform
import os

level_of_controll = 3

def isLinuxOrWindows():
    if platform == "linux" or platform == "linux2":
        return True
    elif platform == "win32":
        return False

if isLinuxOrWindows():
    import alsaaudio
    import pyautogui as pg
elif not isLinuxOrWindows():
    import pywinauto as pw
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

ru_translate = {'ь':'m', 'а':'f', 'б':',', 'в':'d',
       'г':'u', 'д':'l', 'е':'t', 'ё':'`', 'ж':';',
       'з':'p', 'и':'b', 'й':'q', 'к':'r', 'л':'k',
       'м':'v', 'н':'y', 'о':'j', 'п':'g', 'р':'h', 
       'с':'c', 'т':'n', 'у':'e', 'ф':'a', 'х':'[',
       'ц':'w', 'ч':'x', 'ш':'i', 'щ':'o', 'ы':'s',
       'э':"'", 'ю':'.', 'я':'z', 'з':'p'}

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
        if not current_lang:
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
    if str == "up"
    or str == "down"
    or str == "left"
    of str == "right": return "{VK_"+key.upper()+"}"
    return "{"+key.upper()+"}"

app = Flask(__name__)

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
            pw.keyboard.send_keys(translateKeyToWinKey(request.args.get("control")))
    elif request.method=='GET' and request.args.get("text_to_put"):
        text=request.args.get("text_to_put")
        if isLinuxOrWindows():
            writeRaETextLinux(text, control0="win", control1="space")
        elif not isLinuxOrWindows():
            pw.keyboard.send_keys(request.args.get("control"))
    return render_template("index.html", current_volume=getVolume(), level_of_controll=level_of_controll)


def setVolume(volume: int):
    if volume >= 0 and volume <= 100:
        if isLinuxOrWindows():
            m = alsaaudio.Mixer()
            m.setvolume(volume)
        elif not isLinuxOrWindows():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevel(volume, None)
    
def getVolume():
    if isLinuxOrWindows():
        m=alsaaudio.Mixer()
        return m.getvolume()[0]
    return 0

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')