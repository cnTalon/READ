import pyaudio
import wave
import threading

class AudioRecorder(threading.Thread):
	def __init__(self):
		super().__init__()
		self._filename = "sentence.wav"
		self._channels = 1
		self._rate = 16000
		self._frames_per_buffer = 1024
		self._audio = pyaudio.PyAudio()
		self._stream = self._audio.open(format=pyaudio.paInt16,
																		channels=self._channels,
																		rate=self._rate,
																		input=True,
																		frames_per_buffer=self._frames_per_buffer)
		self._frames = []
		self._recording_event = threading.Event() # false by default
		self._finished_flag = False # thread exists until story is finished
	
	
	def start_recording(self):
		if self._stream is None: return print("no stream in recording start attempt")
		self._recording_event.set()
		print("recording")
	
	
	def stop_recording(self):
		if self._stream is None: return print("no stream in recording stop attempt")
		self._recording_event.clear()
		print("stopped")
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
		print("done")
	
	
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
	recorder = AudioRecorder()									# step 1 : make new object
	recorder.start()														# step 2 : start thread
	for _ in range(int(input("input: "))):
		print(_)
		recorder.start_recording()									# step 3 : start the recording i.e. via pressing a button on screen
		try:
			while True:
				pass
		except KeyboardInterrupt:
			pass
		recorder.stop_recording()										# step 5 : stop the recording i.e. via pressing a buttton on screen
	recorder.finish_recording()									# step 6 : repeat steps 3 and 4 until end of story, finally finish recording to end thread's lifecycle
	recorder.join()
