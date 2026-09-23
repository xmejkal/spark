I'm building a battery-powered device on a Seeed XIAO ESP32-C6 with MicroPython. It has two
buttons and a time-of-flight sensor, and it should spend most of its life in deep sleep, waking
when someone presses a button or waves a hand.

Which pins should I put the buttons and the sensor interrupt on, and how do I arm the wake?
