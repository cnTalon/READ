from IPAmatching import IPAmatching
from wav2vec import wav2vec
from story import Story

# initialise
model = wav2vec()
sentence = Story("""One day, a little fish named Fin was swimming on near the shore. Timmy loved to play in the mud. He would jump up and down and make big splashes. One day, Timmy found something unknown in the mud. It was a shiny rock! Timmy was so happy and showed it to his mom. She said it was beautiful and they decided to keep it. From that day on, Timmy would always remember the fun he had playing in the mud and finding the unknown treasure.""").split_into_sentences()[0]
accuracy = 1.0

# recorded
model.load_audio("sentence.wav") 
model.get_values()
input_ipa = model.IPA_transcription
input_eng = model.word_transcription
expected_ipa = IPAmatching.IPA_correction(IPAmatching.ipa_transcription(sentence))

match_list = IPAmatching.pronunciation_matching(input_eng[0],input_ipa[0],expected_ipa.split(),sentence)
words_read = len(match_list)
incorrect_words = []
print(type(match_list[0][2]))
for word in match_list:
    if word[2] == '0':
        accuracy -= 1/words_read # deduct from accuracy if incorrect
        incorrect_words.append(word[0])
print(match_list)
print(incorrect_words)