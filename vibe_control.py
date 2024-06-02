import numpy as np
import pyaudio
import vibrator


#JDC ネットワークの出力ファイルを読み取り、周波数データを取り出す
def getfreq():
    data = []
    filepath = '/home/upoc/upoc/jdcnet/output/pitch_test.wav.txt' # JDCネットワークの出力が格納されている
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()  # 行3先頭と末尾の空白を削除
            if line:  # 空行でない場合のみ処理を行う
                timestamp, frequency = line.split()  # スペースで行を分割
                if float(timestamp)*100 % 5 == 0:
                    data.append((float(timestamp), float(frequency)))
	# データから時間と周波数のリストを作成
    timestamps, frequencies = zip(*data)
    frequencies2 = np.array(frequencies)
    return frequencies2, timestamps


# 周波数データから、音のピッチを表したデータに変換する
def getpitch():
    notes = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
    allnotes = np.arange(-30, 50+1)
    
    pitchs = 440*(np.power(2,(notes-9)/12))
    allpitchs = 440*(np.power(2,(allnotes-9)/12))
    
    result = getfreq()
    freq = result[0]
    octave_multiplier = 2.0
    #rint(freq)
    while np.any(freq != 0) and pitchs.min() > np.min(freq[freq != 0]):
        print(np.min(freq[freq != 0]))
        freq = freq * octave_multiplier
    #print(freq)
        
    # 各値に対して最も近い要素番号を求めて新しい配列に格納
    closest_indices = np.abs(pitchs[:, np.newaxis] - freq).argmin(axis=0)
    # closest_indicesを使用して、最も近い値に対応するpitchsの要素を選択
    closest_pitchs = pitchs[closest_indices]
    closest_pitchs[freq==0] = 0 
    closest_indices[freq==0] = -100

    # 各値に対して最も近い要素番号を求めて新しい配列に格納
    closest_allindices = np.abs(allpitchs[:, np.newaxis] - freq).argmin(axis=0)
    # closest_indicesを使用して、最も近い値に対応するpitchsの要素を選択
    closest_allpitchs = allpitchs[closest_allindices]
    closest_allpitchs[freq==0] = 0

    return closest_indices, closest_allpitchs # 音のピッチの番号と値の配列を返す
    


phase = 0.0  # 初期位相

def play_sound_vibe(vibenum, frequencies, sample_rate=5000): # 音を再生し、その音に対応する振動子を鳴らす
    global phase
    p = pyaudio.PyAudio()
    v = vibrator.vibePattern()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # 音声再生
    for frequency, num in zip(frequencies, vibenum):
        if num == 12: #--------------------音の情報からどの振動子を鳴らすか指定
            v.set_b_values(-100)
        elif num == 24:
            v.set_b_values(num)
        elif num < 12:
            v.set_b_values(num)
        elif num > 12:
            v.set_b_values(num-1)
        #----------------------------------ここまで
        if num != 24:    
            v.vibe()    # 指定した振動子を鳴らす
            
        samples = (0.10 * np.sin(2 * np.pi * ((np.arange(sample_rate/(5))+phase) * frequency / sample_rate))).astype(np.float32) # 鳴らす音の音声波形を構築
        phase += sample_rate/(5)
        stream.write(samples) # 音を鳴らす


    v.set_b_values(-100)
    v.vibe()
    stream.stop_stream()
    stream.close()
    p.terminate()


# play_jdcから、振動子を鳴らす際に呼び出される
def vibe_sound():
    pitchs = getpitch() # JDCネットワークが解析したメロディデータから、ピッチ情報を取り出すプログラムを呼び出す
    num = pitchs[0]
    freq = pitchs[1]
    play_sound_vibe(num, freq) # ピッチ情報から、その音を再生し、音に対応する振動子を鳴らすプログラムを呼び出す



#メイン関数だが、通常は呼ばれない
if __name__ == "__main__": 
    pitchs = getpitch()
    num = pitchs[0]
    freq = pitchs[1]
    play_sound_vibe(num, freq)

