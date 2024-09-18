from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import librosa
from datasets import load_dataset
import torch
from phonemizer.backend.espeak.wrapper import EspeakWrapper
import soundfile as sf


class wav2vec:
    toIPA_tokenizer = None
    toIPA_model = None
    toWord_tokenizer = None
    toWORD_model = None
    PHONEMIZER_ESPEAK_LIBRARY = "C:\Program Files\eSpeak NG\libespeak-ng.dll"
    EspeakWrapper.set_library(PHONEMIZER_ESPEAK_LIBRARY)

    audio = None
    rate = None
    duration = 0.0

    IPA_transcription = None
    word_transcription = None

    def __init__(self):
        # Load model and processor
        self.toIPA_tokenizer = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
        self.toIPA_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")

        self.toWord_tokenizer = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        self.toWORD_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    def load_audio(self, file_name):
        self.audio, self.rate = librosa.load(file_name, sr=16000)
        self.duration += librosa.get_duration(y=self.audio, sr=16000)

    def get_values(self):
        IPA_values = self.toIPA_tokenizer(self.audio, return_tensors="pt").input_values
        word_values = self.toWord_tokenizer(self.audio, return_tensors="pt").input_values
        IPA_logits = self.toIPA_model(IPA_values).logits
        word_logits = self.toWORD_model(word_values).logits
        IPA_prediction = torch.argmax(IPA_logits, dim=-1)
        word_prediction = torch.argmax(word_logits, dim=-1)
        self.IPA_transcription = self.toIPA_tokenizer.batch_decode(IPA_prediction)
        self.word_transcription = self.toWord_tokenizer.batch_decode(word_prediction)
