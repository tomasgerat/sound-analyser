import tensorflow as tf
import csv
import scipy.signal
from scipy.io import wavfile
from wav_tools import SplitWav
from os import listdir
from os.path import isfile, join


class Analyser:
    def __init__(self, model_path, TMP_PATH, sec_per_split=5, overlap=3):
        # Load the model.
        # model = hub.load('https://tfhub.dev/google/yamnet/1')
        self.TMP_PATH = TMP_PATH
        self.sec_per_split = sec_per_split
        self.overlap = overlap
        print("TMP_PATH:", TMP_PATH)
        print("Second per split: ", sec_per_split)
        print("Overlap: ", overlap)
        try:
            print("Try to load model:", model_path)
            self.model = tf.saved_model.load(model_path)
            self.isReady = True
            class_map_path = self.model.class_map_path().numpy()
            self.class_names_model = self.class_names_from_csv(class_map_path)
            self.class_names = self.class_names_model.copy()
            self.class_names.sort()

            '''self.accepted_classes = ["Singing", "Child singing", "Synthetic singing",
                                     "Singing bowl", "Speech", "Child speech", "Speech synthesizer",
                                     "Child speech, kid speaking", "Music"]'''
            self.accepted_classes = []
            print("Done loading model")
        except (ValueError, RuntimeError, TypeError, IOError):
            print("Failed to load model:", model_path)
            self.isReady = False

    def set_accepted_classes(self, classes):
        self.accepted_classes = classes

    def contains_voice(self, filepath):
        sample_rate, wav_data = wavfile.read(filepath, 'rb')
        sample_rate, wav_data = self.ensure_sample_rate(sample_rate, wav_data)

        # Show some basic information about the audio.
        duration = len(wav_data) / sample_rate
        # print(f'Sample rate: {sample_rate} Hz')
        # print(f'Total duration: {duration:.2f}s')
        # print(f'Size of the input: {len(wav_data)}')

        # Listening to the wav file.
        # Audio(wav_data, rate=sample_rate)

        waveform = wav_data / tf.int16.max
        # Run the model, check the output.
        scores, embeddings, spectrogram = self.model(waveform)
        scores_np = scores.numpy()
        spectrogram_np = spectrogram.numpy()

        '''infered_class = self.class_names[scores_np.mean(axis=0).argmax()].lower()
        # print(f'The main sound is: {infered_class}')
        if "speech" in infered_class:
            return True, infered_class'''
        infered_class = self.class_names_model[scores_np.mean(axis=0).argmax()]
        #print(infered_class)
        # print(f'The main sound is: {infered_class}')

        #TODO skontrolovat a radsej pracovat s indexami tried
        if infered_class in self.accepted_classes:
            #print(scores_np.mean(axis=0).argmax())
            return True, infered_class
        return False, infered_class


    def test_file(self, input_f):
        #list of tupples
        detected = []
        notDetected = []
        split_wav = SplitWav(input_f, self.TMP_PATH)
        if split_wav.multiple_split(self.sec_per_split, self.overlap) is True:
            files = [self.TMP_PATH + f for f in listdir(self.TMP_PATH) if isfile(join(self.TMP_PATH, f))]
            files.sort()
            # create a list of vowels

            # 'o' is inserted at index 3 (4th position)
            for f in files:
                # print(f)
                c, infered_class = self.contains_voice(f)
                a = int(f[f.index("_") + 1:len(f) - 4])
                if c is True:
                    print("Speech found in:", f, "Form:", infered_class)
                    print("In original audio:", a, "on: ", (a * 5 - a * 3), "sec")
                    #add found into list
                    detected.append((f, infered_class, a))
                else:
                    print("Speech found in:", f, "Form:", infered_class)
                    print("In original audio:", a, "on: ", (a * 5 - a * 3), "sec")
                    # add not found into list
                    notDetected.append((f, infered_class, a))

        else:
            print("Failed to split: ", input_f)
        return (detected, notDetected)

    # Find the name of the class with the top score when mean-aggregated across frames.
    def class_names_from_csv(self, class_map_csv_text):
        """Returns list of class names corresponding to score vector."""
        class_names = []
        with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row['display_name'])

        return class_names

    def ensure_sample_rate(self, original_sample_rate, waveform,
                           desired_sample_rate=16000):
        """Resample waveform if required."""
        if original_sample_rate != desired_sample_rate:
            desired_length = int(round(float(len(waveform)) /
                                       original_sample_rate * desired_sample_rate))
            waveform = scipy.signal.resample(waveform, desired_length)
        return desired_sample_rate, waveform

    def is_ready(self):
        return self.isReady