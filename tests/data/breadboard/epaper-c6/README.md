The e-paper project of the walk P934 (#1323) on the DFRobot FireBeetle 2 ESP32-C6, as of 2026-11-20 for P957 (#1365):
the walk's `requirements.json` and its draft board file `boards/firebeetle2-esp32c6.json`, with the 14-pin row first.
The e-paper's record is the one in `../epaper/parts/`, which a test copies in. Built with tsci 0.0.2600, this board gets a
pour short from tsci on the MOSI trace that its copper does not make (0.5124 mm apart); `../../pour-contact/` holds
the four elements of that build that show it.
