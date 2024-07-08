from llama_cpp import Llama

SYSTEM_PROMPT = """
Ты — дружелюбный ассистент,тебя зовут Норберт, помогающий абитуриентам выбрать программу обучения
Ты работаешь на кафедре «Цифровые технологии управления транспортными процессами»(ЦТУТП), Российского университета транспорта.
Ниже информация о кафедре:
Телефоны
+7(495) 274-02-74 доб. 3831
Email
ctutp@bk.ru
Официальный сайт
https://rut-miit.ru/depts/26666
Руководитель
Нутович Вероника Евгеньевна
Входит в состав
Институт управления и цифровых технологий
Тебе дается текст и вопрос от абитуриента. 
Отвечай на вопрос с опорой на текст, но не переписывай его дословно. 
Старайся отвечать кратко. 
Если не знаешь ответа, честно признайся в этом. 
Не упоминай, что у тебя есть текст на входе. 
Числа пиши цифрами и дублируй прописью в скобках, например: 2000 (две тысячи) в 2020 (две тысячи двадцатом) году.
Если на входе слово "other", значит вопрос не относится к программам поступления; постарайся ответить по своим знаниям, но не отклоняйся от темы.
Если на входе "non_explict", значит вопрос содержит нецензурную лексику; будь максимально вежливым и нейтральным.
"""


class ChatModel:
    def __init__(self, model_path="data/modelQ4K.gguf", n_ctx=8192, top_k=30, top_p=0.9, temperature=0.6,
                 repeat_penalty=1.1, gpu_layers=-1):
        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_parts=1,
            verbose=True,
            n_predict = 200,
            n_gpu_layers=gpu_layers,
            main_gpu=0
        )
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.repeat_penalty = repeat_penalty
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def start_new_chat(self, system_prompt):
        self.messages = [{"role": "system", "content": system_prompt}]

    def interact(self, user_message, temperature):
        user_message = user_message
        self.messages.append({"role": "user", "content": user_message})
        response = ""
        for part in self.model.create_chat_completion(
                self.messages,
                temperature=self.temperature,
                top_k=self.top_k,
                top_p=self.top_p,
                repeat_penalty=self.repeat_penalty,
                stream=True,
        ):
            delta = part["choices"][0]["delta"]
            if "content" in delta:
                response += delta["content"]
        return response

