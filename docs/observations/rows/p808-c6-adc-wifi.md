# P808: whether the ESP32-C6's one ADC reads with Wi-Fi on: rows

Card: [P808 #1144](https://github.com/xmejkal/spark/issues/1144). A spike: one Sonnet agent read Espressif's own sources
(the finding is the card's comment of 2026-11-13). This file holds the acted, raised and rejected findings only (rules.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | no printed Espressif document says whether the C6's SAR ADC reads with Wi-Fi on | spike | acted | not stated in the datasheet v1.5 §4.2.2.1 p. 57, the TRM v1.2 chapter 39.2, ESP-IDF v5.5.1's esp32c6 `adc_oneshot` and `adc_continuous` pages, or the C6 errata v1.3; the XIAO record's `//adc_gpio` now says so |
| 2 | ESP-IDF's own test reads the C6's ADC1 with Wi-Fi started | spike, checked by the session | acted | `test_adc_wifi.c` at tag v5.5.1: lines 218-224 declare `TEST_CASE("ADC1 work with WiFi")` under `CONFIG_IDF_TARGET_ESP32C6`, and the read before, during and after `esp_wifi_start()` is `adc_work_with_wifi`, lines 182-200 (the PR refuter); sha256 09e8aeefc2144616fb0b073b387c17c264a8a61d29e3a0922d83e591e24a8055 of the raw file; cited in the note by URL, tag, lines and hash. The store keeps PDFs and images only, so the file is not kept |
| 3 | keep the C6 TRM v1.2 | spike | rejected | dropped because it does not state the answer: its chapter 26.4 (p. 728) is about the radio's own high-speed ADC for the RNG, not the SAR ADC |
| 4 | the note's "no ADC pin is lost to the radio" | the session | acted | it stays: `soc_caps.h` v5.5.1 `SOC_ADC_PERIPH_NUM 1` says the chip has one ADC unit, so no ADC2 pin exists to lose |
| 5 | the PR refuter (Opus): the test's comment (lines 219-220) prints a condition the note left out: two modem clocks must be enabled, or the ADC readings are wrong; the read itself is at lines 182-200 | PR review | acted | the note cites lines 182-224 and gains the clause; whether ESP-IDF's driver or MicroPython enables those clocks is not stated by a kept page, so the note claims nothing about it. Confirmed: the hash, the datasheet's §4.2.2.1 (pp. 57-58) and both v5.5.1 esp32c6 ADC pages print no Wi-Fi limit |
