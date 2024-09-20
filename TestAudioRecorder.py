import unittest
from unittest.mock import MagicMock, patch
from audio_recorder import AudioRecorder  # assuming the code is saved in a file named 'audio_recorder.py'
import threading

class TestAudioRecorder(unittest.TestCase):

    @patch('pyaudio.PyAudio')
    def setUp(self, MockPyAudio):
        # Mock PyAudio and stream object
        self.mock_audio = MockPyAudio.return_value
        self.mock_stream = MagicMock()
        self.mock_audio.open.return_value = self.mock_stream
        
        self.recorder = AudioRecorder()

    def test_initialization(self):
        # Test if attributes are correctly initialized
        self.assertEqual(self.recorder._filename, "sentence.wav")
        self.assertEqual(self.recorder._channels, 1)
        self.assertEqual(self.recorder._rate, 16000)
        self.assertEqual(self.recorder._frames_per_buffer, 1024)
        self.assertIsInstance(self.recorder._audio, MagicMock)
        self.assertIsInstance(self.recorder._stream, MagicMock)
        self.assertEqual(self.recorder._frames, [])
        self.assertFalse(self.recorder._recording_event.is_set())
        self.assertFalse(self.recorder._finished_flag)

    def test_start_recording(self):
        # Test if recording starts properly
        self.recorder.start_recording()
        self.assertTrue(self.recorder._recording_event.is_set())
        self.assertEqual(self.mock_stream.start_stream.call_count, 0)  # Stream not started here

    def test_stop_recording(self):
        # Test stopping recording
        self.recorder._frames.append(b'some audio data')
        with patch('wave.open', new_callable=MagicMock) as mock_wave_open:
            self.recorder.stop_recording()
            self.assertFalse(self.recorder._recording_event.is_set())
            self.assertEqual(mock_wave_open.call_count, 1)  # Ensure wave file opened and written
            self.assertEqual(self.recorder._frames, [])  # Frames cleared after saving

    def test_finish_recording(self):
        # Test finishing recording
        self.recorder.finish_recording()
        self.assertTrue(self.recorder._finished_flag)
        self.assertTrue(self.recorder._recording_event.is_set())

    def test_get_filename(self):
        # Test getFilename method
        self.assertEqual(self.recorder.getFilename(), "sentence.wav")

    @patch('pyaudio.PyAudio')
    def test_run_method(self, MockPyAudio):
        # Test the run method to simulate audio streaming
        self.recorder._recording_event.set()
        self.recorder._finished_flag = False

        with patch.object(self.recorder._stream, 'read', return_value=b'some audio data'):
            with patch.object(self.recorder, '_save_recording', return_value=None):
                def stop_thread_after_delay():
                    import time
                    time.sleep(1)
                    self.recorder._finished_flag = True
                    self.recorder._recording_event.set()

                stop_thread = threading.Thread(target=stop_thread_after_delay)
                stop_thread.start()

                self.recorder.run()  # Run should process data until stop thread ends
                self.assertGreater(len(self.recorder._frames), 0)
                stop_thread.join()

    @patch('pyaudio.PyAudio')
    def tearDown(self, MockPyAudio):
        self.recorder._audio.terminate()

if __name__ == '__main__':
    unittest.main()
