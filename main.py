from ctc_interface import SpeechRecognizer
from lama_interface import ChatModel
from classificator_interface import QuestionClassifier

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
        bobr.interact(question, temperature=0.0)

        prev_context = context
finally:
    recognizer.close()