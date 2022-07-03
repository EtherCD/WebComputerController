from flask import *
from sys import platform

if platform == "linux" or platform == "linux2":
    import alsaaudio
elif platform == "win32":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)

@app.route("/", methods = ['POST', 'GET'])
def index():
    if request.method=='GET' and request.args.get("volume"):
        volume:int = request.args.get("volume")
        print(volume)
        setVolume(int(volume))
    return render_template("index.html", current_volume=getVolume())

def setVolume(volume: int):
    if volume >= 0 and volume <= 100:
        if platform == "linux" or platform == "linux2":
            m = alsaaudio.Mixer()
            m.setvolume(volume)
        elif platform == "win32":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevel(volume, None)
    
def getVolume():
    if platform == "linux" or platform == "linux2":
        m=alsaaudio.Mixer()
        return m.getvolume()[0]
    return 0

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
