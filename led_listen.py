import pyaudio
import wave
import RPi.GPIO as GPIO
import webrtcvad
import requests
import subprocess
from secret import token

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 1
CHUNK = 320
INPUT_DEVICE = 2    #change to suit your setup
SHORT_NORMALIZE = (10.0 / 32768.0)
LEDPIN = 16


def setup_pins():
    # set up the Raspberry Pi output pins for the led lighting
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LEDPIN, GPIO.OUT)
    GPIO.setwarnings(False)
    GPIO.output(LEDPIN, GPIO.LOW)


def setup_audio():
    #set up parameters and open stream for recording, also initialises voice detection
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input_device_index=INPUT_DEVICE,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK)
    vad = webrtcvad.Vad()
    vad.set_mode(3)  # aggressiveness is 0=least to 3=highest
    print("Setup complete")
    return stream, p, vad


def led_on():
    GPIO.output(LEDPIN, GPIO.HIGH)
    print('LED on')


def led_off():
    GPIO.output(LEDPIN, GPIO.LOW)


def get_data(stream):
    data = stream.read(CHUNK, exception_on_overflow=False)
    return data


def write_file(frames, p):
    #code to write the output file when audio has been detected using input as frames
    filename = 'outfile.wav'
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return filename


def transcribe(filename):
    # posts a recording to koreromaori.io - requires that audio file is in the same folder as this code
    print('Transcribing...')
    api_url = "https://koreromaori.io/api/transcription/?method=stream"
    kwargs = {
        'headers': {
            'Authorization': 'Token {0}'.format(token)
        },
        'files': {
            'audio_file': open(filename, 'rb')
        },
        'data': {
            'name': filename
        }
    }
    response = requests.post(api_url, **kwargs)
    response_dict = response.json()

    if response.status_code == 201:
        return response_dict.get('transcription')
    else:
        return -1


def said_kia_ora(words):
    result = 0
    phrase1 = 'kia ora'.split(' ')
    if compare_phrases(words, phrase1):
        result = 1
    return result


def compare_phrases(words, phrase):
    ##checks if all items in a list of words of phrase are included in list of heard words
    result = 0
    intersect = set(words) & set(phrase)
    if intersect == set(phrase):
        result = 1
    return result


def asked_for_news_phrase(words):
    #identifies if the phrase spoken is included in one of those expected
    asked_news = 0
    phrase1 = u'he aha ng{a} take o te w{a} ki Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase2 = u'Whakap{a}hongia ng{a} p{u}rongo k{o}rero o Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase3 = u'Whakap{a}hotia ng{a} p{u}rongo k{o}rero o Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase4 = u'Whakap{a}hotia ng{a} p{u}rongo k{o}rero o te motu'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase5 = u'Whakatairangahia ng{a} p{u}rongo k{o}rero o te w{a}'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase6 = u'Whakatairangatia ng{a} kaupapa o te w{a} ki Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase7 = u'He aha ng{a} kaupapa o te w{a} ki Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase8 = u'He aha ng{a} p{u}rongo k{o}rero {a} motu'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase9 = 'kua pau te hau'.lower().split()
    for phrase in (phrase1, phrase2, phrase3, phrase4, phrase5, phrase6, phrase7, phrase8, phrase9):
        if compare_phrases(words, phrase):
            asked_news = 1
    return asked_news


def asked_for_news(words):
    #identifies if the phrase spoken is included in one of those expected
    asked_news = 0
    count = 0
    max = len(words)
    pt1 = 0
    pt2 = 0
    list1 = u'aha whakatairangahia whakap{a}hongia whakap{a}hotia'.format(a = u"\u0101").split(' ')
    list2 = u'take p{u}rongo kaupapa'.format(u = u"\u016B").split(' ')
    list3 = u'motu w{a} tokerau'.format(a = u"\u0101").split(' ')
    for i in range(count, max):
        if words[i] in list1:
            pt1 = 1
            count = i
    if pt1 == 1:
        for i in range(count, max):
            if words[i] in list2:
                pt2 = 1
                count = i
    if pt2 == 1:
        for i in range(count, max):
            if words[i] in list3:
                asked_news = 1
    return asked_news


def asked_for_radio(words):
    asked_radio = 0
    count = 0
    max = len(words)
    pt1 = 0
    pt2 = 0
    list1 = u'whakatairangahia whakatairangatia whakap{a}hongia whakap{a}hotia'.format(a = u"\u0101").split(' ')
    for i in range(count, max):
        if words[i] in list1:
            pt1 = 1
            count = i
    if pt1 == 1 and i >= 2:
        for i in range(count, max):
            if words[i-2] == 'te' and words[i-1] == "reo" and words[i] == 'irirangi':
                pt2 = 1
                count = i
    if pt2 == 1:
        for i in range(count, max):
            if words[i] == "muriwhenua":
                asked_radio = 1
            elif words[i] == 'ika':
                if words[i-3] == 'hiku' and words[i-2] == 'o' and words[i-1] == 'te':
                    asked_radio = 1
    return asked_radio


def get_regional_news():
    kwargs = {}
    api_url = "https://tehiku.nz/api/te-reo/nga-take/latest"
    response = requests.get(api_url, **kwargs)
    response_dict = response.json()
    media = response_dict['media'][0]
    media_link = media['media_file']
    media_len = media['duration'] / 100
    print("Latest news is {} seconds long".format(media_len))
    return media_link, media_len


def play_me_the_news():
    media_link, media_len = get_regional_news()
    subprocess.run(["mplayer", media_link])
    led_on()


def finish(stream, p):
    stream.stop_stream()
    stream.close()
    p.terminate()
    GPIO.cleanup()


def main():
    setup_pins()
    (stream, p, vad) = setup_audio()
    count = 0
    quiet_count = 0
    loud_count = 0
    frames = []

    while 1:
        try:
            frame = get_data(stream)
            contains_speech = vad.is_speech(frame, RATE)
            if contains_speech:
                loud_count += 1
                if quiet_count != 0:
                    quiet_count = 0
                frames.append(frame)

            elif contains_speech == 0:
                if loud_count < 8 and quiet_count > 2 and frames != []:
                    loud_count = 0
                    frames = []
                quiet_count += 1

                if quiet_count > 20 and loud_count != 0:
                    frames = []
                    loud_count = 0

                if quiet_count >= 20 and loud_count > 50 and frames != []:
                    audio_file = write_file(frames, p)
                    frames = []
                    loud_count = 0
                    unsplit_words = transcribe(audio_file)
                    words = unsplit_words.split(" ")
                    print('I heard: ', unsplit_words)
                    if words != '':
                        if said_kia_ora(words):
                            flash(4)
                        elif asked_for_news(words):
                            play_me_the_news()
                        elif asked_for_news_phrase(words):
                            print('You said an exact phrase!!')
                            play_me_the_news()
                        elif asked_for_radio(words):
                            subprocess.Popen(["mplayer", "http://radio.tehiku.live:8030/stream;1"])
        except Exception as e:
            finish(stream, p)
            print('Exception:  ', e)
            break

    finish(stream, p)
    print('Done recording')

main()
