import serial
import subprocess
import sys
import time
PORT = "/dev/cu.usbmodem101"
def opened():
    for _ in range(50):
        try: return serial.Serial(PORT, 115200, timeout=0.1)
        except (OSError, serial.SerialException): time.sleep(0.2)
def read_for(s, secs):
    out, t = b"", time.time()
    while time.time() - t < secs:
        try: out += s.read(512)
        except serial.SerialException: return out + b"<port dropped>"
    return out
def mp():
    r = subprocess.run([sys.executable, "-m", "mpremote", "connect", PORT, "exec", "print('hi')"], capture_output=True, text=True, timeout=40)
    return r.returncode == 0
for wait in (0, 1, 3):
    s = opened(); s.dtr = False; s.rts = True; time.sleep(0.1); s.rts = False
    boot = read_for(s, 3); s.close(); time.sleep(wait)
    print("RTS reset with port open, ready %-5s, close, wait %d s, mpremote answers: %s" % (b"ready" in boot, wait, mp()), flush=True)
