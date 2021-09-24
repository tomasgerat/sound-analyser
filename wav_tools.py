from pydub import AudioSegment
import math


class SplitWav:
    def __init__(self, filepath, TMP_PATH):
        self.filepath = filepath
        self.TMP_PATH = TMP_PATH

        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_sec, to_sec, split_filepath):
        t1 = from_sec * 1000
        t2 = to_sec * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(split_filepath, format="wav")

    def get_digits_cnt(self, num):
        cnt = 0
        while (num / 10) >= 1:
            num /= 10
            cnt += 1
        return cnt

    def prepend_zeroes(self, num, digits):
        output = ""
        for i in range(0, digits - self.get_digits_cnt(num)):
            output += "0"
        output += str(num)
        return output

    def multiple_split(self, sec_per_split, overlap=0):
        total_secs = math.ceil(self.get_duration())
        step = sec_per_split-overlap
        if step < 1:
            print("[Error] Split step: ", step)
            return False
        success = False
        num = 0
        digits = self.get_digits_cnt(math.ceil(total_secs / float(step)))
        for i in range(0, total_secs, step):
            split_fn = self.TMP_PATH + "tmp_" + self.prepend_zeroes(num, digits) + ".wav"
            self.single_split(i, i + sec_per_split, split_fn)
            #print(str(i) + ' Done')
            success = True
            num += 1
        return success
