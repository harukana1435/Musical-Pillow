import sys
sys.path.append('/home/upoc/.local/lib/python3.9/site-packages/')
import play_jdc
import play_snd
import RPi.GPIO as GPIO
import time
import os

# GPIOのピン番号
BUTTON_PIN1 = 17 #青
BUTTON_PIN2 = 18 #黒
PIN_BUTTON_SD = 18 # シャットダウンボタン PIN2と同じ

def button_callback0(channel): # BUTTON_PIN1が押されたときに、歌声を解析するプログラムを呼び出す。
    GPIO.remove_event_detect(BUTTON_PIN1)
    os.system("/usr/bin/python3 /home/upoc/upoc/play_jdc.py 0")
    GPIO.add_event_detect(BUTTON_PIN1, GPIO.FALLING, callback=button_callback0, bouncetime=200)


def button_callback1(channel): # BUTTON_PIN2が押されたときに、演奏方法を提示するプログラムを呼び出す。ボタンを3秒以上連続で押した場合は、楽器枕をシャットダウンする。
    GPIO.remove_event_detect(BUTTON_PIN2)
    if channel == PIN_BUTTON_SD:
        sw = 0 # 3秒以上長押しされたかどうか検知するフラグ
        for _ in range(15):
            time.sleep(0.2) # 0.2秒 × 15回 = 3秒
            sw = GPIO.input(channel)
            if sw == 1: # 15回中１回でもLOWがあればシャットダウンしない
                break
        if sw == 0:
            os.system('sudo shutdown -h now') # シャットダウン
            time.sleep(2)
    os.system("/usr/bin/python3 /home/upoc/upoc/play_jdc.py 1")
    GPIO.add_event_detect(BUTTON_PIN2, GPIO.FALLING, callback=button_callback1, bouncetime=200)
 


def main():
    # インスタンスの作成
    snd = play_snd.Play_SND() # 音を鳴らす機能
    jdc = play_jdc.Play_JDC() # 歌声を解析する機能

    #電子楽器としての機能を実行
    snd.exe_play_snd()

    # GPIOの初期設定
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # コールバックの設定
    GPIO.add_event_detect(BUTTON_PIN1, GPIO.FALLING, callback=button_callback0, bouncetime=200)
    GPIO.add_event_detect(BUTTON_PIN2, GPIO.FALLING, callback=button_callback1, bouncetime=200)


if __name__ == '__main__':
    main()
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            GPIO.cleanup()
