import RPi.GPIO as GPIO
import time

data_pin1 = 21  # シリアルデータ1
latch_pin1 = 20  # ラッチクロック1
clock_pin1 = 19  # シフトレジスタクロック1

pin12 = 5 #12番目の振動子のピンが5
pin24 = 6 #24番目の振動子のピンが6

# ピンをセットする
GPIO.setmode(GPIO.BCM)
GPIO.setup(data_pin1,GPIO.OUT)
GPIO.setup(latch_pin1,GPIO.OUT)
GPIO.setup(clock_pin1,GPIO.OUT)
GPIO.setup(pin12,GPIO.OUT)
GPIO.setup(pin24,GPIO.OUT)

#bool
alltrue= int('11111111',2)

class vibePattern:
	
	def __init__(self):
		self.b1= 0
		self.b2= 0
		self.b3 =0
		print('vibe Pattern start')

	# ピッチ情報からどの振動子を鳴らすか決める関数
	def set_b_values(self, value): # 音のピッチに対して、どの振動子を鳴らすかを決めている
		#do re mi.. =  7 6 5 4 ...
		if 0 <= value <= 7:
			b1 = 1 << (7 - value)
			self.b1 = int(format(b1 & alltrue,'08b'),2 )
		elif 8 <= value <= 15:
			b2 = 1 << (15 - value)
			self.b2 = int(format(b2 & alltrue,'08b') ,2 )
		elif 16 <= value <= 23:
			b3 = 1 << (23 - value)	
			self.b3 = int(format(b3 & alltrue,'08b') ,2 )
		elif value == 24:
			GPIO.output(pin24,GPIO.HIGH)
		elif value == -100:
			self.b1 = 0
			self.b2 = 0
			self.b3 = 0
			GPIO.output(pin24,GPIO.LOW)


	# 振動子を鳴らす関数
	def vibe(self):
		GPIO.output(latch_pin1, GPIO.LOW)
		# それぞれのセグメントは電子回路上の列を表している
		# 3列目
		for i in range (8):
			GPIO.output(clock_pin1,GPIO.LOW)
			GPIO.output(data_pin1,(self.b3 >> i)&1)
			GPIO.output(clock_pin1,GPIO.HIGH)
			 

		#2列目
		for i in range (8):
			GPIO.output(clock_pin1,GPIO.LOW)
			GPIO.output(data_pin1,(self.b2 >> i)&1)
			GPIO.output(clock_pin1,GPIO.HIGH)

		#1列目
		for i in range (8):
			GPIO.output(clock_pin1,GPIO.LOW)
			GPIO.output(data_pin1,(self.b1 >> i)&1)
			GPIO.output(clock_pin1,GPIO.HIGH)

		GPIO.output(latch_pin1, GPIO.HIGH) # 指定した振動子を鳴らす


# メイン関数だが、通常は呼び出されない
if __name__ == "__main__":
	test = vibePattern()
	'''
	n = 19
	test.set_b_values(n)
	if n!=24:
		test.vibe()
	time.sleep(3)
	print("a")
	test.set_b_values(-100)
	test.vibe()
	'''
	for i in range(25):
		#print("asdfasdf"+str(i))
		test.set_b_values(i)
		test.vibe()
		time.sleep(0.5)
		test.set_b_values(-100)
		test.vibe()
		time.sleep(1)
	
	GPIO.cleanup()
