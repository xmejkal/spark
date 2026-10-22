"""P238 spike rows: each resets the XIAO, sends bytes, and logs what came back. Nothing is erased or written."""
import serial
import subprocess
import sys
import time
PORT = "/dev/cu.usbmodem101"
def log(*a): print(*a, flush=True)
def pulse(s): s.dtr = False; s.rts = True; time.sleep(0.1); s.rts = False
def read_for(s, secs):
    out, t = b"", time.time()
    while time.time() - t < secs: out += s.read(512)
    return out
def ctrl_c(s):
    s.write(b"\x03"); return read_for(s, 1.5)
def row(name, sent, got):
    log("%-48s sent %-22r -> prompt %-5s %r" % (name, sent, b">>>" in got, got[-50:]))
s = serial.Serial(PORT, 115200, timeout=0.1)
pulse(s); boot = read_for(s, 3); row("E0 RTS reset, port open, read boot", b"", boot)
row("E1 then Ctrl-C at once", b"\x03", ctrl_c(s))
pulse(s); read_for(s, 3); time.sleep(10); s.reset_input_buffer()
row("E2 RTS reset, idle 10 s, Ctrl-C", b"\x03", ctrl_c(s))
pulse(s); read_for(s, 3); s.write(b"a" * 300); time.sleep(0.5)
row("E3 RTS reset, 300 bytes 'a', then Ctrl-C", b"a*300 + \\x03", ctrl_c(s))
row("E3b a second Ctrl-C", b"\x03", ctrl_c(s))
pulse(s); boot = read_for(s, 3)
row("E4 RTS reset clears it? Ctrl-C", b"\x03", ctrl_c(s))
s.close()
subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32c6", "-p", PORT, "chip-id"], capture_output=True)
r = subprocess.run([sys.executable, "-m", "mpremote", "connect", PORT, "exec", "print('hi')"], capture_output=True, text=True, timeout=30)
row("E5 esptool reset, then mpremote at once", b"\\r\\x03\\r\\x01 (mpremote)", (r.stdout + r.stderr[-60:]).encode())
s = serial.Serial(PORT, 115200, timeout=0.1)
row("E6 then pyserial, Ctrl-C", b"\x03", ctrl_c(s))
pulse(s); read_for(s, 3); s.close()
r = subprocess.run([sys.executable, "-m", "mpremote", "connect", PORT, "exec", "print('hi')"], capture_output=True, text=True, timeout=30)
row("E7 RTS reset with port open, then mpremote", b"(mpremote)", (r.stdout + r.stderr[-60:]).encode())
