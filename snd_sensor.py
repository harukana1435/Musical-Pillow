from socket import *
import RPi.GPIO as GPIO
from gpiozero import MCP3208

Vref = 5 # 接触位置センサの最大電圧
BUZZER_PIN = 17 # ブザーのピン

GPIO.setmode(GPIO.BCM)

def setup(): # テスト時にブザーの出力先を指定する
    GPIO.setup(BUZZER_PIN, GPIO.OUT)


def analog_read(channel): # 接触位置センサから0~5Vの電圧を受け取る関数
    pot = MCP3208(channel)
    volt = pot.value * Vref
    return volt


def poscal(): # 2つの接触位置センサの位置情報を渡す関数
    i_value0 = analog_read(0)
    i_value1 = analog_read(1)
    return i_value0, i_value1


# メイン関数だが通常は呼び出されない
if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        GPIO.cleanup()
