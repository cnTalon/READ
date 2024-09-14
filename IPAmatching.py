from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper
import string
from itertools import product

# Set up phonemizer with the path to the espeak library
PHONEMIZER_ESPEAK_LIBRARY = "C:\Program Files\eSpeak NG\libespeak-ng.dll"
EspeakWrapper.set_library(PHONEMIZER_ESPEAK_LIBRARY)

# Define a dictionary to correct IPA phonetic transcriptions
IPA_CORRECTION_DICTIONARY = {
    'oː': 'ɔː',
    'ə': 'æ',
    'ɔ': 'ɑː'
}

# Define a dictionary for phonetic representations of various sounds
phonetic_dict = {
    # Consonants
    'b': ['b'],
    'd': ['d', 'dd'],
    'dʒ': ['j', 'dg', 'g'],
    'f': ['f'],
    'g': ['g', 'gg'],
    'ɡ': ['g', 'gg'],
    'h': ['h'],
    'k': ['k', 'c', 'ck', 'ke'],
    'l': ['l', 'll'],
    'm': ['m', 'mm'],
    'n': ['n', 'nn'],
    'ŋ': ['n', 'ng'],
    'p': ['p', 'pp'],
    'r': ['r', 'rr'],
    's': ['s', 'ss', 'c'],
    'ʃ': ['sh', 'ti'],
    't': ['t', 'tt'],
    'ɾ': ['t', 'tt'],
    'tʃ': ['t', 'tch', 'ch'],
    'θ': ['th'],
    'ð': ['th'],
    'v': ['v'],
    'w': ['w'],
    'ʰw': ['wh'],
    'j': ['y', 'i'],
    'z': ['z', 'zz'],
    'ʒ': ['s', 'ge'],

    # Vowels
    'æ': ['a', 'e', 'o', 'ow'],
    'eɪ': ['a', 'ay', 'ai'],
    'ɐ': ['u', 'a'],
    'ɑ': ['a', 'o'],
    'ʌ': ['a', 'u', 'o'],
    'ɛər': ['air', 'are', 'ear'],
    'ɔ': ['o', 'r', 'aw', 'or', 'a'],
    'ɹ': ['r', 'ar', 're'],
    'aʊər': ['hour'],
    'ɛ': ['e', 'ea', 'a'],
    'i': ['e', 'ea', 'y'],

    'ɪər': ['ear', 'e', 'eer'],
    'ər': ['er', 'erer'],
    'ɜr': ['ear', 'ir', 'irr'],
    'aɪ': ['i', 'y'],
    'aɪər': ['ire'],
    'ɒ': ['o', 'a'],
    'oʊ': ['ow', 'oa'],
    'aʊ': ['ow', 'oa', 'o', 'ou'],
    'uː': ['ou', 'oo', 'ue'],
    'ʊ': ['oo', 'u', 'ou'],

    'ɔɪ': ['oi', 'oy'],
    'ə': ['a', 'e', 'us', 'o'],
    'a': ['a', 'i'],
    'ɪ': ['i', 'e', 'eer', 'ear', 'y']
}


class IPAmatching:
    # Translator to remove punctuation
    translator = str.maketrans('', '', string.punctuation)

    # List for storing correction data (not used directly in this code)
    correction_list = []

    @staticmethod
    def ipa_transcription(text):
        """
        Convert text to IPA transcription using phonemizer.
        """
        return phonemize(
            text,
            language='en-us',  # Use 'en-gb' for UK English
            backend='espeak',
            strip=True
        )

    @staticmethod
    def remove_punctuation(text):
        """
        Remove all punctuation characters from the input text.
        """
        return text.translate(IPAmatching.translator)

    @staticmethod
    def IPA_correction(phonetics):
        """
        Correct IPA phonetic transcriptions based on a predefined dictionary.
        """
        phonetics = phonetics.split()
        corrected_phonetics = [IPA_CORRECTION_DICTIONARY.get(p, p) for p in phonetics]
        return ' '.join(corrected_phonetics)

    @staticmethod
    def correct_original_phonetics(phonetics):
        """
        Correct specific phonetic representations.
        """
        corrected_phonetics = []
        for phoneme in phonetics.split():
            if phoneme == 'aɪɐm':
                corrected_phonetics.extend(['aɪ', 'ɐm'])
            else:
                corrected_phonetics.append(phoneme)
        return ' '.join(corrected_phonetics)

    @staticmethod
    def set_text_index(original):
        """
        Create a list of indices corresponding to each word in the original text.
        """
        return list(enumerate(original.split()))

    @staticmethod
    def set_matching_value(original):
        """
        Initialize matching values for each word in the original text.
        """
        original = IPAmatching.remove_punctuation(original)
        return [[word, '-', '-'] for word in original.split()]

    @staticmethod
    def pronunciation_matching(original_STT, original_STI, converted_TTI, original):
        """
        Match the pronunciation between the original and converted texts.
        """
        original_STT = IPAmatching.remove_punctuation(original_STT).split()

        original = IPAmatching.remove_punctuation(original)
        original_STI = IPAmatching.IPA_correction(original_STI)
        match_list = IPAmatching.set_matching_value(original)
        IPA_list = original_STI.split()
        temp_list = []

        for i in range(len(IPA_list)):
            if IPA_list[i] in phonetic_dict:
                temp_list.append(phonetic_dict[IPA_list[i]])

        # Update match_list with matching status for original_STT
        for i, (word, _, _) in enumerate(match_list):
            match_list[i][1] = '1' if i < len(original_STT) and original_STT[i].lower() == word.lower() else '0'

        IPA_form_list = []
        index = 0
        for i in range(len(match_list)):
            IPA_form = IPAmatching.ipa_transcription(match_list[i][0])
            if i == 0:
                IPA_form_list.append([IPA_form, 0, len(IPA_form) + 5])
                index = len(IPA_form)
            elif i == len(match_list) - 1:
                index += len(IPA_form)
                IPA_form_list.append([IPA_form, index - 10, index])
            else:
                if i == 1:
                    lower = index - len(IPAmatching.ipa_transcription(match_list[0][0]))
                    IPA_form_list.append([IPA_form, lower, index + len(IPA_form) + 5])
                else:
                    IPA_form_list.append([IPA_form, index - 5, index + len(IPA_form) + 5])
                index += len(IPA_form)

        # Match IPA forms with the original STI
        for i in range(len(match_list)):
            IPA_form = IPAmatching.ipa_transcription(match_list[i][0])

            start_index = IPA_form_list[i][1]
            end_index = IPA_form_list[i][2]
            # Check if indices are within the bounds of the original_STI
            if start_index < 0:
                start_index = 0
            if end_index > len(original_STI):
                end_index = len(original_STI)

            # Extract the substring from original_STI
            substring = "".join(original_STI.split())
            substring = substring[start_index:end_index]

            if IPA_form in substring:
                match_list[i][2] = '1'
            else:
                substring = "".join(substring)
                substring = substring.replace("ː", "")
                result = IPAmatching.check_permutation(list(substring.replace('ː', '')), match_list[i][0])
                if result == '1':
                    match_list[i][2] = '1'
                else:
                    match_list[i][2] = '0'

        return match_list

    @staticmethod
    def check_permutation(IPA_list, word):
        """
        Check if any permutation of IPA_list matches the given word.
        """
        IPA_form = IPAmatching.ipa_transcription(word)
        IPA_key_values = []
        for i in range(len(IPA_list)):
            if IPA_list[i] in phonetic_dict:
                IPA_key_values.append(phonetic_dict[IPA_list[i]])
        for i in range(len(IPA_list)):
            IPA_NO = IPA_key_values[i:i + len(IPA_form) - 1]
            IN_combinations = product(*IPA_NO)
            IPA_Zero = IPA_key_values[i:i + len(IPA_form)]
            IZ_combinations = product(*IPA_Zero)
            IPA_One = IPA_key_values[i:i + len(IPA_form) + 1]
            IO_combinations = product(*IPA_One)
            IPA_Two = IPA_key_values[i:i + len(IPA_form) + 2]
            IT_combinations = product(*IPA_Two)

            # Check if any combination matches the word
            for combination in IN_combinations:
                tr = ''.join(combination)
                if tr == word.lower():
                    return '1'
            for combination in IZ_combinations:
                tr = ''.join(combination)
                if tr == word.lower():
                    return '1'
            for combination in IO_combinations:
                tr = ''.join(combination)
                if tr == word.lower():
                    return '1'
            for combination in IT_combinations:
                tr = ''.join(combination)
                if tr == word.lower():
                    return '1'
