import threading

import flet as ft
import time
from main import handle_voice_input, get_answer, classify_question, synthesize_speech, record_and_transcribe
animation_on = False  # global variable to track animation state


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message, is_bot: bool = False, text_size: int = 16):
        super().__init__()
        self.vertical_alignment = "start"
        self.alignment = ft.MainAxisAlignment.END if is_bot else ft.MainAxisAlignment.START

        message_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD, size=text_size),
                    ft.Text(message.text, selectable=True, size=text_size),
                ],
                tight=True,
                spacing=5,
            ),
            padding=15,
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            expand=True,
            expand_loose=True,
        )

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name), size=text_size),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            message_container,
        ]

        if is_bot:
            self.controls.reverse()

    def get_initials(self, name: str) -> str:
        if name is None:
            return 'S'
        return ''.join([part[0].upper() for part in name.split()])

    def get_avatar_color(self, name: str) -> str:
        colors = [ft.colors.RED, ft.colors.GREEN, ft.colors.BLUE]
        return colors[hash(name) % len(colors)]


def main(page: ft.Page):
    page.window.full_screen = True
    page.horizontal_alignment = "stretch"
    page.title = "Информационный бот кафедры"

    gradient = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=["#7c7cd6", "#5c5dc7"],
    )

    welcome_message = Message(
        user_name="Норберт",
        text="Приветствую! Я ваш информационный бот. Как я могу помочь вам сегодня?",
        message_type="bot_message"
    )

    def animate():
        global animation_on
        animation_on = not animation_on  # toggle animation state
        if animation_on:
            def run_animation():
                global animation_on
                while animation_on:

                    animated_background.scale = 2
                    page.update()
                    time.sleep(0.2)  # delay to see the animation

                    animated_background.scale = 1
                    page.update()
                    time.sleep(0.2)  # delay to see the animation

            # Start animation in a separate thread
            threading.Thread(target=run_animation).start()

    def handle_voice():
        global animation_on
        animate()
        transcription = record_and_transcribe()
        animation_on = False
        voice_button.icon = ft.icons.MIC
        voice_container.border = None
        page.update()

        user_message = Message("Студент", transcription, message_type="chat_message")
        page.pubsub.send_all(user_message)
        page.update()
        answer = handle_voice_input(transcription)
        bot_response = Message("Норберт", answer, message_type="bot_message")
        page.pubsub.send_all(bot_response)
        page.update()
        synthesize_speech(answer)

    def on_message(message: Message):
        text_size = 16
        if page.width < 800:
            text_size = 20
        elif page.width > 1200:
            text_size = 24
        if message.message_type == "chat_message":
            m = ChatMessage(message, text_size=text_size)
        else:
            m = ChatMessage(message, is_bot=True, text_size=text_size)
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(on_message)
    page.pubsub.send_all(welcome_message)

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    voice_button = ft.IconButton(
        icon=ft.icons.MIC,
        icon_size=128,
        tooltip="Голосовое сообщение",
        bgcolor=ft.colors.WHITE,
        on_click=lambda e: handle_voice(),
    )

    animated_background = ft.Container(
        bgcolor=ft.colors.with_opacity(0.2, ft.colors.GREY),
        shape=ft.BoxShape.CIRCLE,
        width=132,
        height=132,
        animate_scale=ft.animation.Animation(200, ft.AnimationCurve.LINEAR),
    )

    voice_container = ft.Container(
        content=voice_button,
        shape=ft.BoxShape.CIRCLE,
        animate_scale=ft.animation.Animation(200, ft.AnimationCurve.LINEAR),
        bgcolor=ft.colors.with_opacity(0.5, "#ffffff"),
    )

    voice_stack = ft.Stack(
        controls=[
            animated_background,
            voice_container,
        ],
        alignment=ft.alignment.center,
    )

    image = ft.Image(
        src="data/iudt.png",
        width=256,
        height=256,
    )

    image_container = ft.Container(
        content=image,
        alignment=ft.alignment.center,
        padding=10,
    )

    chat_container = ft.Container(
        content=chat,
        expand=True,
        padding=10,
    )

    bottom_container = ft.Container(
        content=ft.Row(
            controls=[voice_stack],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=72,
    )

    gradient_container = ft.Container(
        content=ft.Column(
            [
                image_container, chat_container, bottom_container
            ],
            tight=True,
            spacing=5,
        ),
        gradient=gradient,
        expand=True,
    )

    page.add(gradient_container)


ft.app(target=main)
