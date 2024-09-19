from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper
import string
from itertools import product

# Path to the eSpeak library, used by the phonemizer for IPA transcription
PHONEMIZER_ESPEAK_LIBRARY = "C:\Program Files\eSpeak NG\libespeak-ng.dll"

# Set the eSpeak library path in the EspeakWrapper for phonemizer
EspeakWrapper.set_library(PHONEMIZER_ESPEAK_LIBRARY)

# Dictionary for correcting certain IPA symbols to a more standardized form
IPA_CORRECTION_DICTIONARY = {
    'oː': 'ɔː',
    'ə': 'æ',
    'ɔ': 'ɑː'
}

# Phonetic dictionary mapping IPA symbols to common English spelling patterns
phonetic_dict = {
    # Consonants and their common English spelling patterns
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
    'ɾ': ['t', 'tt'],  # Flap, often heard in American English
    'tʃ': ['t', 'tch', 'ch'],
    'θ': ['th'],
    'ð': ['th'],
    'v': ['v'],
    'w': ['w'],
    'ʰw': ['wh'],
    'j': ['y', 'i'],
    'z': ['z', 'zz', 's'],
    'ʒ': ['s', 'ge', 'zh'],  # 'zh' for some accents
    'ʔ': ['?'],  # Glottal stop
    'ʍ': ['wh'],  # Voiceless 'w' sound, often heard in some dialects
    'tɹ': ['tr'],  # Common in American English for 'tr' sound
    'dɹ': ['dr'],  # Common in American English for 'dr' sound
    'ɬ': ['ll'],  # Voiceless lateral fricative (found in Welsh)
    'ɮ': ['ll'],  # Voiced lateral fricative (found in some languages)

    # Vowels and their common English spelling patterns
    'æ': ['a', 'e', 'o', 'ow'],
    'eɪ': ['a', 'ay', 'ai'],
    'ɐ': ['u', 'a', 'o'],
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
    'ə': ['a', 'e', 'us', 'o', 'er'],
    'a': ['a', 'i'],
    'ɪ': ['i', 'e', 'eer', 'ear', 'y'],
    'ɚ': ['ir'],
    'o': ['a'],
    'ʉ': ['oo'],  # Close central rounded vowel
    'ø': ['eu'],  # Close-mid front rounded vowel
    'œ': ['e', 'eu'],  # Open-mid front rounded vowel
    'iː': ['ee', 'ea'],  # Long 'i' sound, often seen in words like 'see' or 'beat'
    'u': ['oo', 'ou', 'u', 'ew'],  # Short 'u' sound

    # Diphthongs and their common English spelling patterns
    'eə': ['air', 'are'],
    'ɔʊ': ['o', 'ou'],
    'ɪə': ['ear', 'e'],
    'ʊə': ['oor', 'ure'],
    'əʊ': ['o'],  # Another representation for the 'o' sound in some accents

    # Additional IPA symbols and their English spelling patterns
    'ɕ': ['ch'],  # Voiceless alveolo-palatal fricative, common in some languages
    'ʑ': ['j'],  # Voiced alveolo-palatal fricative, common in some languages
    'ŋ̊': ['ng'],  # Voiceless nasal, found in some accents
    'tʃʰ': ['ch'],  # Aspirated voiceless postalveolar affricate
    'dʒʰ': ['j'],  # Aspirated voiced postalveolar affricate

    # Various accents and regional variations
    'aː': ['ah'],  # Long 'a' sound
    'eː': ['ee'],  # Long 'e' sound
    'oː': ['oh'],  # Long 'o' sound
    'ɔː': ['aw', 'or'],  # Long 'aw' sound

    # Common letter patterns and contractions
    'ɹ̩': ['r'],  # Syllabic 'r', common in some dialects
    'ɪɹ': ['ir'],  # Common in words like 'bird'
    'ɛɹ': ['er'],  # Common in words like 'her'
    'ʌɹ': ['ur'],  # Common in words like 'fur'
}


class IPAmatching:
    # Translator table to remove punctuation from text
    translator = str.maketrans('', '', string.punctuation)

    @staticmethod
    def ipa_transcription(text, cache={}):
        """
        Convert text to IPA transcription using caching to avoid repeated calls.

        Parameters:
        - text: The input text to convert to IPA.
        - cache: A dictionary to cache the results of previous transcriptions.

        Returns:
        - The IPA transcription of the input text.
        """
        if text not in cache:
            # Perform IPA transcription and store the result in cache
            cache[text] = phonemize(
                text,
                language='en-us',
                backend='espeak',
                strip=True
            )
        return cache[text]

    @staticmethod
    def remove_punctuation(text):
        """
        Remove punctuation from the given text using the translator table.

        Parameters:
        - text: The input text from which to remove punctuation.

        Returns:
        - The text with punctuation removed.
        """
        return text.translate(IPAmatching.translator)

    @staticmethod
    def IPA_correction(phonetics):
        """
        Correct IPA symbols to their standardized forms using a correction dictionary.

        Parameters:
        - phonetics: The input IPA transcription to be corrected.

        Returns:
        - The corrected IPA transcription.
        """
        # Split the IPA transcription into symbols and apply corrections
        phonetics = phonetics.split()
        corrected_phonetics = [IPA_CORRECTION_DICTIONARY.get(p, p) for p in phonetics]
        return ' '.join(corrected_phonetics)

    @staticmethod
    def pronunciation_matching(original_STT, original_STI, converted_TTI, original):
        """
        Match the pronunciation of text segments using IPA transcription and compare results.

        Parameters:
        - original_STT: The original speech-to-text transcription.
        - original_STI: The original IPA transcription of the text.
        - converted_TTI: The converted IPA transcription to compare against.
        - original: The original text for reference.

        Returns:
        - A list of match results indicating the match status of each word.
        """
        # Remove punctuation and prepare the original texts
        original_STT = IPAmatching.remove_punctuation(original_STT).split()
        original = IPAmatching.remove_punctuation(original)
        original_STI = IPAmatching.IPA_correction(original_STI)

        # Initialize match list with placeholder values
        match_list = [[word, '-', '-'] for word in original.split()]
        IPA_list = original_STI.split()

        # Cache IPA transcriptions for words in the match list
        IPA_transcriptions = {word: IPAmatching.ipa_transcription(word) for word, _, _ in match_list}

        # Check if each word in original_STT matches the corresponding word in the match list
        for i, (word, _, _) in enumerate(match_list):
            match_list[i][1] = '1' if i < len(original_STT) and original_STT[i].lower() == word.lower() else '0'

        # Create a list of IPA forms with their indices in the original STI
        IPA_form_list = []
        index = 0
        for i, (word, _, _) in enumerate(match_list):
            IPA_form = IPA_transcriptions[word]
            start_index = max(index - 5, 0) if i != 0 else 0
            end_index = min(index + len(IPA_form) + 5, len(original_STI))
            IPA_form_list.append([IPA_form, start_index, end_index])
            index += len(IPA_form)

        # Remove spaces from the original STI transcription
        original_STI_str = "".join(original_STI.split())

        # Compare IPA forms against segments of the original STI transcription
        for i in range(len(match_list)):
            IPA_form = IPA_transcriptions[match_list[i][0]]
            start_index, end_index = IPA_form_list[i][1:3]
            substring = original_STI_str[start_index:end_index]

            if IPA_form in substring:
                match_list[i][2] = '1'
            else:
                # Remove long vowel marker and check permutations
                substring = substring.replace("ː", "")
                result = IPAmatching.check_permutation(list(substring), match_list[i][0])
                match_list[i][2] = '1' if result == '1' else '0'

        return match_list

    @staticmethod
    def check_permutation(IPA_list, word):
        """
        Check if a permutation of the given IPA list can match the word.

        Parameters:
        - IPA_list: A list of IPA symbols to check.
        - word: The word to match against the permutations.

        Returns:
        - '1' if a permutation matches, otherwise '0'.
        """
        IPA_form = IPAmatching.ipa_transcription(word)
        IPA_key_values = [phonetic_dict.get(ipa, []) for ipa in IPA_list]
        word_lower = word.lower()

        # Check permutations of IPA segments to see if they match the word
        for i in range(len(IPA_list)):
            for length in range(len(IPA_form) - 1, len(IPA_form) + 2):
                if i + length <= len(IPA_list):
                    IPA_segment = IPA_key_values[i:i + length]
                    all_combinations = set(''.join(combination) for combination in product(*IPA_segment))
                    if word_lower in all_combinations:
                        return '1'
        return '0'
