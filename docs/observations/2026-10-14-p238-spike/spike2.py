import serial, subprocess, sys, time
PORT = "/dev/cu.usbmodem101"
def opened():
    for _ in range(50):
        try: return serial.Serial(PORT, 115200, timeout=0.1)
        except (OSError, serial.SerialException): time.sleep(0.2)
    raise SystemExit("port never came back")
def read_for(s, secs):
    out, t = b"", time.time()
    while time.time() - t < secs:
        try: out += s.read(512)
        except serial.SerialException: return out + b"<port dropped>"
    return out
def row(name, got): print("%-52s -> prompt %-5s %r" % (name, b">>>" in got or b"hi" in got, got[-60:]), flush=True)
def mp():
    r = subprocess.run([sys.executable, "-m", "mpremote", "connect", PORT, "exec", "print('hi')"], capture_output=True, text=True, timeout=40)
    return (r.stdout + " | " + (r.stderr.strip().splitlines() or [""])[-1]).encode()
time.sleep(2); s = opened()
s.dtr = False; s.rts = True; time.sleep(0.1); s.rts = False; row("E4 reset with port open after the full ring", read_for(s, 3))
s.close(); s = opened(); s.write(b"\x03"); row("E4b then Ctrl-C", read_for(s, 1.5)); s.close()
for name, settle in (("E5 esptool reset, mpremote at once", 0), ("E5b esptool reset, mpremote after 5 s", 5)):
    subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32c6", "-p", PORT, "chip-id"], capture_output=True)
    time.sleep(settle); row(name, mp())
    row(name + ", mpremote again", mp())
subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32c6", "-p", PORT, "chip-id"], capture_output=True)
s = opened(); got = read_for(s, 3); row("E6 esptool reset, pyserial reads 3 s", got)
s.write(b"\x03"); row("E6b then Ctrl-C", read_for(s, 1.5)); s.close()
