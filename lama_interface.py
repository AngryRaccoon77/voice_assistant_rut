from llama_cpp import Llama

SYSTEM_PROMPT = "Ты дружелюбный ассистент, ты помогаешь абитуриентам определится с выбором программы обучения. На вход ты получаешь текст и вопрос от абитуриента. Отвечай на вопрос с опорой на текст . Не переписывай текст. Старайся ответить как можно короче. Ты отвечаешь на вопросы касательно образовательных программ кафедры цифровые технологии управления транспортными процессами Российского университета транспорта (МИИТ)."


class ChatModel:
    def __init__(self, model_path="data/modelQ4K.gguf", n_ctx=8192, top_k=30, top_p=0.9, temperature=0.6,
                 repeat_penalty=1.1, gpu_layers=0):
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

