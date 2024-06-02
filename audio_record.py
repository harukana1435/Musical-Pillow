import pyaudio
import wave
import sounddevice


p = pyaudio.PyAudio()
for i in range(p.get_device_count()): # 録音マイクのデバイスを探している
    audiodev = p.get_device_info_by_index(i)
    if "USB PnP Sound Device: Audio" in audiodev['name']:
        index = audiodev['index']

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz　サンプリング周波数
chunk = 32 # 2^12 一度に取得するデータ数
record_secs = 15 # 録音する秒数
dev_index = index # デバイス番号
wav_output_filename = '/home/upoc/upoc/record/test.wav' # 出力するファイル



def audio_record():
	audio = pyaudio.PyAudio()

	# pyaudioストリームの作成
	stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
	print("recording")
	frames = []

	# 録音中
	for i in range(0,int((samp_rate/chunk)*record_secs)):
		data = stream.read(chunk)
		frames.append(data)

	print("finished recording")

	stream.stop_stream()
	stream.close()
	audio.terminate()

	# 録音した音声をファイルに保存
	wavefile = wave.open(wav_output_filename,'wb')
	wavefile.setnchannels(chans)
	wavefile.setsampwidth(audio.get_sample_size(form_1))
	wavefile.setframerate(samp_rate)
	wavefile.writeframes(b''.join(frames))
	wavefile.close()

# メイン関数だが、通常は呼び出されない
if __name__=="__main__":
	audio_record()
	

