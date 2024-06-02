import numpy as np
import pyaudio
import struct
import threading
import snd_sensor as sensor

class Play_SND:

    def __init__(self):
        self.RATE = 5000
        self.bufsize = 128
        #各種パラメータ用スライダーの設定
        self.sl=np.array([0,150,100,50,0,0,0,0])
        self.slName = np.array(['Wave_type',
                    'Attack',
                    'Release',
                    'Lowpass_freq',
                    'FM_amp',
                    'FM_freq',
                    'Delay_time',
                    'Delay_feedback'])
        
        self.keyon = [0, 0]
        self.pre_keyon = [0, 0]
        self.pitch = [440, 440]
        self.pre_pitch = [440, 440]
        self.velosity = [0.0, 0.0]
        self.keys = [np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,12]), np.array([12,13,14,15,16,17,18,19,20,21,22,23,24,24])]
        self.betweens =  [0.10, 0.30, 0.50, 0.80,1.0,1.3,1.5,1.8,2.0,2.3,2.5,2.8,3.0,3.2]
        self.betweens_range = 0.05
        self.betweens_flag = [0, 0]
        self.betweens_cur = [0, 0]
        self.ringbuf = [np.zeros(50000), np.zeros(50000)] # 最大ディレイタイムは50000/RATE秒
        self.waveform = [np.arange(self.bufsize), np.arange(self.bufsize)] # 波形が格納されている
        self.waveform_pos = [0, 0]
        self.playing = 1 # 演奏可能かどうか 
        self.sl = [0, 150, 100, 50, 0, 0, 0, 0]


    def touch_event(self): # 接触位置センサの情報から鳴らす音を決める
        sensor_value = sensor.poscal() # 接触位置センサの値を受け取る
        touch_pos = [int(sensor_value[0] * 10), int(sensor_value[1] * 10)] # 値を0~10にスケールする

        for i in range(2):
            if (self.betweens_flag[i] == 1) and (self.betweens_cur[i]-self.betweens_range < sensor_value[i]) and (sensor_value[i] < self.betweens_cur[i]+self.bitweens_range):
                self.pitch[i] = self.pre_pitch[i]
                print(self.pitch[i])
            elif (self.betweens_flag[i] == 1) and not(self.betweens_cur[i]-self.betweens_range < sensor_value[i] and sensor_value[i] < self.betweens_cur[i] + self.betweens_range):
                self.betweens_flag[i] = 0

            if self.betweens_flag[i] == 0:
                if touch_pos[i] != 0 and touch_pos[i] < 32:
                    self.keyon[i] = 1
                    note = self.keys[i][int((touch_pos[i]/32)*(len(self.keys[i])-1))]
                    self.pitch[i] = 440 * (np.power(2, (note-9)/12))
                    self.pre_pitch[i] = self.pitch[i]
                else:
                    self.keyon[i] = 0
                    self.betweens_flag[i] = 0
            if self.pre_keyon[i] == 0 and self.keyon[i] == 1:
                self.velosity[i] = 0.0
            self.pre_keyon[i] = self.keyon[i]

        for between in self.betweens:
            for i in range(2):
                if (between-self.betweens_range < sensor_value[i]) and (sensor_value[i] < between + self.betweens_range) and (self.betweens_flag[i] == 0):
                    self.betweens_flag[i] = 1
                    self.betweens_cur[i] = between
  
    



    def synthesize(self): # あるピッチに対応する音声波形を生成する

        wave = [None, None]

        for i in range(2):
            #位相計算
            t = self.pitch[i] * (self.waveform[i]+self.waveform_pos[i]) / self.RATE
            t = t - np.trunc(t)
            self.waveform_pos[i] += self.bufsize

            #基本波形選択
            if self.sl[0]==1:#のこぎり波
                wave[i] = t*2.0-1.0
            elif self.sl[0]==2:#矩形波
                wave[i] = np.zeros(self.bufsize)
                wave[i][t<=0.5]=-1
                wave[i][t>0.5]=1
            elif self.sl[0]==3:#三角波
                wave[i] = np.abs(t*2.0-1.0)*2.0-1.0
            elif self.sl[0]==4:#FM変調
                wave[i] = np.sin(2.0*np.pi*t + self.sl[4]/100.0 * np.sin(2.0*np.pi*t*self.sl[5]))
            else:#サイン波
                wave[i] = np.sin(2.0*np.pi*t)

            #エンベロープ設定
            if self.keyon[i] == 1:
                vels = self.velosity[i] + self.waveform * ((self.sl[1]/1000)**3+0.00001)
                vels[vels>0.6] = 0.6
            else:
                vels = self.velosity[i] - self.waveform * ((self.sl[2]/1000)**3+0.00001)
                vels[vels<0.0] = 0.0
            self.velosity[i] = vels[-1]    
            wave[i] = vels * wave[i]

        return wave



    def delay(self, wave): # 音声波形にディレイエフェクトを加える
        delaytime = self.sl[6]/255.0 * 1.0
        feedback = self.sl[7]/255.0 * 0.7
        dryandwet = feedback/2.0
        writepoint = int(delaytime*self.RATE)

        outwave = [None, None]

        for i in range(2):
            self.ringbuf[i] = np.roll(self.ringbuf[i],-self.bufsize)
            self.ringbuf[i][writepoint:writepoint+self.bufsize] = wave[i] + feedback * self.ringbuf[i][:self.bufsize]
            outwave[i] = (1-dryandwet) * wave[i] + dryandwet * self.ringbuf[i][:self.bufsize]

        return outwave

    

    def audioplay(self): # 音を鳴らす
        print ("Start Streaming")
        p=pyaudio.PyAudio()
        stream=p.open(format = pyaudio.paInt16,
                channels = 2,
                rate = self.RATE,
                frames_per_buffer = self.bufsize,
                output = True)
        while stream.is_active():
            self.touch_event() # 接触位置センサの情報から、どの音を鳴らすか決める

            buf = self.synthesize() # 鳴らす音に対応した音声波形を生成する
            buf = self.delay(buf) # 音声波形に対してディレイのエフェクトを適用する
            buf = (buf * 32768.0).astype(np.int16) # 音声波形をスケールする

            interleaved = np.column_stack((buf[0], buf[1])).ravel() # 2つの音声波形を繋ぎ合わせる
            packed_data = struct.pack("h" * len(interleaved), *interleaved) 
            stream.write(packed_data) # 音を鳴らす
    
            if self.playing == 0:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()
        print ("Stop Streaming")



    def exe_play_snd(self): # 楽器枕が起動したときに呼び出される
        thread = threading.Thread(target=self.audioplay)
        thread.start()
    

#メイン関数だが、通常は呼び出されない
if __name__ == "__main__": 
    jdc = Play_SND()
    jdc.exe_play_snd()

    
