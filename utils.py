import wave
import pyaudio
from ctc_interface import SpeechRecognizer
from lama_interface import ChatModel
from classificator_interface import QuestionClassifier
from vosk_tts import Model, Synth

# Инициализация моделей и классов
model = Model(model_name="vosk-model-tts-ru-0.6-multi")
synth = Synth(model)
classificator = QuestionClassifier()
bobr = ChatModel()
recognizer = SpeechRecognizer()


SYSTEM_PROMPT_MAIN = """
Ты — дружелюбный ассистент, помогающий абитуриентам выбрать программу обучения. 
Тебе дается текст и вопрос от абитуриента. 
Отвечай на вопрос с опорой на текст, но не переписывай его дословно. 
Старайся отвечать кратко. 
Если не знаешь ответа, честно признайся в этом. 
Не упоминай, что у тебя есть текст на входе. 
Числа пиши цифрами и дублируй прописью в скобках, например: 2000 (две тысячи) в 2020 (две тысячи двадцатом) году.
Если на входе слово "other", значит вопрос не относится к программам поступления; постарайся ответить по своим знаниям, но не отклоняйся от темы.
Если на входе "non_explict", значит вопрос содержит нецензурную лексику; будь максимально вежливым и нейтральным.
"""


# Калибровка микрофона
recognizer.calibrate_microphone()

def play_audio(filename):
    """Функция воспроизведения аудио файла"""
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()

def record_and_transcribe():
    """Функция записи и распознавания голоса"""
    transcription = recognizer.listen_and_transcribe()
    return transcription

def classify_question(question):
    """Функция классификации вопроса"""
    context = classificator.classify_question(question=question)
    return context

def get_answer(context, question):
    """Функция получения ответа от модели"""
    question_with_context = f"Текст:{context} \n Вопрос:{question}"
    answer = bobr.interact(question_with_context, temperature=0.0)
    return answer

def synthesize_speech(text, filename="out.wav"):
    """Функция синтеза речи"""
    synth.synth(text, filename, speaker_id=3)
    play_audio(filename)

prev_context = ""

def handle_voice_input(transcription):
    """Функция обработки голосового ввода"""
    global prev_context
    context = classify_question(transcription)
    if context == "prev_message":
        context = prev_context
    if prev_context != context:
        bobr.start_new_chat(system_prompt=SYSTEM_PROMPT_MAIN)
    answer = get_answer(context, transcription)
    prev_context = context
    print(answer)
    return answer, context