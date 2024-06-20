import flet as ft

from lama_interface import ChatModel
from main import handle_voice_input, get_answer, classify_question, synthesize_speech, record_and_transcribe


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

import flet as ft

import flet as ft

class ChatMessage(ft.Row):
    def __init__(self, message: Message, is_bot: bool = False):
        super().__init__()
        self.vertical_alignment = "start"
        self.alignment = ft.MainAxisAlignment.END if is_bot else ft.MainAxisAlignment.START

        # Создание градиентного фона
        gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#7c7cd6", "#5c5dc7"],
        )

        # Определение контейнера с градиентным фоном и переносом текста
        message_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
            padding=10,
            border_radius=8,
            gradient=gradient,
            expand=True,  # Растягивание контейнера
            width=100  # Установка фиксированной ширины контейнера
        )

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            message_container,
        ]

        if is_bot:
            self.controls.reverse()

    def get_initials(self, name: str) -> str:
        return ''.join([part[0].upper() for part in name.split()])

    def get_avatar_color(self, name: str) -> str:
        # Пример функции для генерации цвета аватара на основе имени
        colors = [ft.colors.RED, ft.colors.GREEN, ft.colors.BLUE]
        return colors[hash(name) % len(colors)]

def main(page: ft.Page):
    bert = ChatModel
    message_from_bot = ""
    message_to_bot = ""
    page.horizontal_alignment = "stretch"
    page.title = "Информационный бот кафедры"

    # Welcome Message from Bot
    welcome_message = Message(
        user_name="Bobr",
        text="Приветствую! Я ваш информационный бот. Как я могу помочь вам сегодня?",
        message_type="bot_message"
    )

    def join_chat_click(e):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        else:
            page.session.set("user_name", join_user_name.value)
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{join_user_name.value}: ")
            page.pubsub.send_all(Message(user_name=join_user_name.value, text=f"{join_user_name.value} присоединился", message_type="login_message"))
            page.pubsub.send_all(welcome_message)
            page.update()

    def send_message_click(e):
        if new_message.value != "":
            user_message = Message(page.session.get("user_name"), new_message.value, message_type="chat_message")
            bert = ChatModel()  # Instantiate your Bertbober class here
            message_from_bot = new_message.value
            message_to_bot = get_answer(context=classify_question(message_from_bot), question=message_from_bot)
            if message_to_bot == "[CLS]" or message_to_bot == "":
                message_to_bot = "Пожалуйста, задайте вопрос лучше!"
            if message_from_bot == "Как тебя зовут?":
                message_to_bot = "Привет, дорогой друг! Я голосовой помощник по имени Bobr, готов ответить на твои вопросы!"
            if message_from_bot == "Как с вами связаться?":
                message_to_bot = "Контактная информация руководителя программы «Технологии искусственного интеллекта в транспортных системах» : info@ctutp.ru"
            if message_from_bot == "Как подать документы?":
                message_to_bot = "Необходимо в офисе приемной комиссии получить данные авторизации в окне и затем, послать документы через цифровой портал rut-miit, контактная почта - info@ctutp.ru"
            page.pubsub.send_all(user_message)
            bot_response = Message("Bobr", message_to_bot, message_type="bot_message")
            page.pubsub.send_all(bot_response)
            new_message.value = ""
            new_message.focus()
            page.update()

    def handle_voice():
        transcription = record_and_transcribe()
        """Функция обработки голосового ввода"""
        user_message = Message(page.session.get("user_name"), transcription, message_type="chat_message")
        page.pubsub.send_all(user_message)
        page.update()
        answer = handle_voice_input(transcription)
        bot_response = Message("Bobr", answer, message_type="bot_message")
        page.pubsub.send_all(bot_response)
        new_message.value = ""
        new_message.focus()
        page.update()
        synthesize_speech(answer)

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "bot_message":
            m = ChatMessage(message, is_bot=True)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12)
        chat.controls.append(m)
        page.update()


    page.pubsub.subscribe(on_message)

    join_user_name = ft.TextField(
        label="Как к вам можно обрщаться?",
        autofocus=True,
        on_submit=join_chat_click,
    )
    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Привет!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Задать вопрос", on_click=join_chat_click)],
        actions_alignment="end",
    )

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text="Написать сообщение",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    voice_button = ft.IconButton(
        icon=ft.icons.MIC,
        tooltip="Голосовое сообщение",
        on_click=lambda e: handle_voice(),
    )
    voice_button.start_animation = lambda: voice_button.animate(
        "scale",
        1.2,
        duration=500,
        curve=ft.curves.EASE_IN_OUT,
        repeat=True,
    )
    voice_button.stop_animation = lambda: voice_button.animate(
        "scale",
        1.0,
        duration=500,
        curve=ft.curves.EASE_IN_OUT,
    )

    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                voice_button,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Отправить сообщение",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.app(main)