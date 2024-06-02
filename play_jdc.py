import pyaudio
import numpy as np
from audio_record import audio_record
import subprocess
from vibe_control import vibe_sound
import sys



class Play_JDC:
 
	def __init__(self):
		self.timestamps = None
		self.frequencies = None
		self.JDC_command = ["python", "melodyExtraction_JDC.py", "-p", "../record/test.wav", "-o", "./output/"] # JDCネットワークを実行するコマンド
		self.working_directry = "/home/upoc/upoc/jdcnet/" # 現在のワーキングディレクトリ


	# 起動音や操作が完了した音を再生する関数
	def check_sound(self, sample_rate=5000):
		frequencies = [1000]*10
		p = pyaudio.PyAudio()
		stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

		# 音声再生
		for frequency in frequencies:
			samples = (0.10*(np.sin(2 * np.pi * np.arange(sample_rate/(5)) * frequency / sample_rate))).astype(np.float32)
			stream.write(samples)

		stream.stop_stream()
		stream.close()
		p.terminate()



	def jdc_exe(self): #歌声からメロディを抽出するAIを実行する
		# subprocessを使用してコマンドを実行
		try:
			result = subprocess.run(
				self.JDC_command,
				cwd=self.working_directory,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)
			# コマンドの実行結果を表示
			print("Standard Output:", result.stdout)
			print("Standard Error:", result.stderr)
    
		except subprocess.CalledProcessError as e:
			print("Error:", e)



	def exe_play_jdc(self, button): # 楽器枕のボタンが押されたときに呼び出される
		self.check_sound() # ボタンが押されたことをユーザに教える
		if button == 0: # ----------------------楽器枕のボタン1が押されたときだけ実行される
			print("recording-start")
			audio_record() #ユーザの歌声を録音するプログラムを呼び出す
			print("recording-finish")
			self.check_sound() # 録音が終了したことをユーザに教える
			self.jdc_exe() # 歌声からメロディを抽出するAIを呼び出す
			print("jdc-finish")
		# --------------------------------------ここまで
		print("play-sound_vibe")
		vibe_sound() # 振動で演奏方法を提示するプログラムを呼び出す。また、演奏対象となるメロディを再生する



#メイン関数だが通常は呼び出されない
if __name__ == "__main__":
	play_jdc = Play_JDC()
	play_jdc.exe_play_jdc(int(sys.argv[1]))

