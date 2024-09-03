import pyaudio
import wave
import threading

class AudioRecorder(threading.Thread):
  def __init__(self):
    super().__init__()
    self._filename = "recording.wav"
    self._channels = 1
    self._rate = 16000
    self._frames_per_buffer = 1024
    self._audio = pyaudio.PyAudio()
    self._stream = self._audio.open(format=pyaudio.paInt16,
                                    channels=self._channels,
                                    rate=self._rate,
                                    input=True,
                                    frames_per_buffer=self._frames_per_buffer,
                                    start=False) # stream started by start_recording()
    self._frames = []
    self._recording_event = threading.Event() # false by default
    self._finished_flag = False # thread exists until story is finished
  
  
  def start_recording(self):
    if self._stream is None: return print("no stream in recording start attempt")
    self._stream.start_stream()
    self._recording_event.set()
  
  
  def stop_recording(self):
    if self._stream is None: return print("no stream in recording stop attempt")
    self._recording_event.clear()
    self._stream.stop_stream()
    self._save_recording()
  
  
  def _save_recording(self):
    with wave.open(self._filename,"wb") as _sound_file:
      _sound_file.setnchannels(self._channels)
      _sound_file.setsampwidth(self._audio.get_sample_size(pyaudio.paInt16))
      _sound_file.setframerate(self._rate)
      _sound_file.writeframes(b''.join(self._frames))
    self._frames.clear()
  
  
  def finish_recording(self):
    self._finished_flag = True
    self._recording_event.set()
  
  
  def getFilename(self):
    return self._filename
  
  
  def run(self):
    if self._stream is None: return print("no stream in recording run attempt")
    while True:
      self._recording_event.wait()
      if self._finished_flag: break
      try:
        data = self._stream.read(self._frames_per_buffer)
        self._frames.append(data)
      except Exception as e:
        print(f"error in recording run: {e}")
        break
    self._stream.stop_stream()
    self._stream.close()
    self._audio.terminate()


if __name__ == "__main__":
  recorder = AudioRecorder()
  recorder.start()
  recorder.start_recording()
  import time
  for _ in range(2):
    time.sleep(1)
    print((_+1).__str__() + " seconds")
  recorder.stop_recording()
  recorder.finish_recording()
  print("done")
  recorder.join()