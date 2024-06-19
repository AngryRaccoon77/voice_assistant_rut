import wave

import pyaudio

from ctc_interface import SpeechRecognizer
from lama_interface import ChatModel
from classificator_interface import QuestionClassifier

from vosk_tts import Model, Synth

def play_audio(filename):
    # Открываем файл
    wf = wave.open(filename, 'rb')

    # Создаем объект PyAudio
    p = pyaudio.PyAudio()

    # Открываем поток для воспроизведения
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Читаем данные
    data = wf.readframes(1024)

    # Воспроизводим аудио
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)

    # Останавливаем поток
    stream.stop_stream()
    stream.close()

    # Закрываем PyAudio
    p.terminate()


model = Model(model_name="vosk-model-tts-ru-0.6-multi")
synth = Synth(model)


classificator = QuestionClassifier()
bobr = ChatModel()
recognizer = SpeechRecognizer()
recognizer.calibrate_microphone()

SYSTEM_PROMT_MAIN = "Ты дружелюбный ассистент, ты помогаешь абитуриентам определится с выбором программы обучения. На вход ты получаешь текст и вопрос от абитуриента. Отвечай на вопрос обязательно с опорой на текст. Не переписывай текст в точности. Старайся ответить как можно короче"
SYSTEM_PROMT_TALK = "Ты дружелюбный ассистент, ты помогаешь абитуриентам определится с выбором программы обучения. Старайся ответить как можно короче. Ты отвечаешь на вопросы касательно образовательных программ кафедры ЦТУТП Российского университета транспорта"
try:
    while True:
        prev_context = ""
        user_input = input("Press 'Enter' to start recording or type 'exit' to quit: ").strip()
        if user_input.lower() == 'exit':
            break
        transcription = recognizer.listen_and_transcribe()
        recognizer.close()


        context = classificator.classify_question(question=transcription)
        if context == "prev_message":
            context = prev_context
        elif context == "other":
            bobr.start_new_chat(system_prompt=SYSTEM_PROMT_TALK)
        if prev_context != context:
            bobr.start_new_chat(system_prompt=SYSTEM_PROMT_MAIN)
        print(context)

        question = f"Текст:{context} \n Вопрос:{transcription}"
        answer = bobr.interact(question, temperature=0.0)
        synth.synth(answer, "out.wav", speaker_id=2)
        prev_context = context
        play_audio("out.wav")
finally:
    recognizer.close()