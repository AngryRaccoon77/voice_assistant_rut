import threading
import flet as ft
import time
import csv
from main import handle_voice_input, record_and_transcribe, synthesize_speech


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

    def log_interaction(self, question, answer, rating):
        with open('interactions.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([ question, answer, rating])


class ChatMessage(ft.Row):
    def __init__(self, message: Message, chat, page, is_bot: bool = False, text_size: int = 16):
        super().__init__()
        self.chat = chat
        self.page = page
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
            self.controls.append(
                ft.Row(
                    controls=[
                        ft.IconButton(ft.icons.THUMB_UP, on_click=lambda e: self.rate_message(message, "like")),
                        ft.IconButton(ft.icons.THUMB_DOWN, on_click=lambda e: self.rate_message(message, "dislike"))
                    ]
                )
            )
            self.controls.reverse()

    def get_initials(self, name: str) -> str:
        return ''.join([part[0].upper() for part in name.split()]) if name else 'S'

    def get_avatar_color(self, name: str) -> str:
        colors = [ft.colors.RED, ft.colors.GREEN, ft.colors.BLUE]
        return colors[hash(name) % len(colors)]

    def rate_message(self, message, rating):
        last_user_message = [m for m in self.chat.controls if isinstance(m, ChatMessage) and not m.alignment == ft.MainAxisAlignment.END][-1]
        question = last_user_message.controls[1].content.controls[1].value
        answer = message.text
        message.log_interaction(question, answer, rating)
        self.page.update()


def main(page: ft.Page):
    global chat

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

    def animate_listing(animation_state):
        if animation_state["running"]:
            def run_animation():
                while animation_state["running"]:
                    animated_background.scale = 2
                    page.update()
                    time.sleep(0.2)
                    animated_background.scale = 1
                    page.update()
                    time.sleep(0.2)
            threading.Thread(target=run_animation).start()

    def animate_think(animation_state):
        if animation_state["running"]:
            def run_animation():
                while animation_state["running"]:
                    c1.opacity = 0.2
                    c1.update()
                    c3.opacity = 1
                    c3.update()
                    time.sleep(0.4)

                    c2.opacity = 0.2
                    c2.update()
                    c1.opacity = 1
                    c1.update()
                    time.sleep(0.4)

                    c3.opacity = 0.2
                    c3.update()
                    c2.opacity = 1
                    c2.update()
                    time.sleep(0.4)
                c1.opacity = 1
                c2.opacity = 1
                c3.opacity = 1
                page.update()
            threading.Thread(target=run_animation).start()

    def animate_say(animation_state):
        if animation_state["running"]:
            def run_animation():
                while (animation_state["running"]):
                    circle_say1.scale = 1.25
                    circle_say2.scale = 1.25
                    page.update()
                    time.sleep(0.175)  # delay to see the animation
                    circle_say1.scale = 1
                    circle_say2.scale = 1
                    page.update()
                    time.sleep(0.175)  # delay to see the animation

            threading.Thread(target=run_animation).start()

    def handle_voice():
        animation_state_listing = {"running": True}
        animate_listing(animation_state_listing)
        transcription = record_and_transcribe()
        animation_state_listing["running"] = False

        user_message = Message("Студент", transcription, message_type="chat_message")
        page.pubsub.send_all(user_message)
        page.update()

        switch.content = think_container
        switch.update()
        animation_state_think = {"running": True}
        animate_think(animation_state_think)
        answer = handle_voice_input(transcription)
        animation_state_think["running"] = False

        bot_response = Message("Норберт", answer, message_type="bot_message")
        page.pubsub.send_all(bot_response)
        page.update()

        switch.content = stack_say
        switch.update()
        animation_state_say = {"running": True}
        animate_say(animation_state_say)
        synthesize_speech(answer)
        animation_state_say["running"] = False

        switch.content = voice_stack
        switch.update()

    def on_message(message: Message):
        text_size = 16 if page.width < 800 else 20 if page.width <= 1200 else 24
        chat_message = ChatMessage(message, chat, page, is_bot=(message.message_type == "bot_message"), text_size=text_size)
        chat.controls.append(chat_message)
        page.update()

    page.pubsub.subscribe(on_message)
    page.pubsub.send_all(welcome_message)

    chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    c1 = ft.Container(
        width=20,
        height=20,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="#186694",
        border_radius=10,
        animate_opacity=400,
    )
    c2 = ft.Container(
        width=20,
        height=20,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="#186694",
        border_radius=10,
        animate_opacity=400,
    )
    c3 = ft.Container(
        width=20,
        height=20,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="#186694",
        border_radius=10,
        animate_opacity=400,
    )

    row = ft.Row(controls=[c1, c2, c3], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
    think_container = ft.Container(
        content=row,
        shape=ft.BoxShape.CIRCLE,
        expand=True,
        bgcolor="white",
        height=132,
        width=132,
    )

    circle_say1 = ft.Container(
        width=100,
        height=100,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="#186694",
        border_radius=5,
        animate_scale=ft.animation.Animation(200, ft.AnimationCurve.BOUNCE_IN_OUT),
    )
    circle_say2 = ft.Container(
        width=50,
        height=50,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="white",
        border_radius=5,
        animate_scale=ft.animation.Animation(200, ft.AnimationCurve.BOUNCE_IN_OUT),
    )
    circle_say3 = ft.Container(
        shape=ft.BoxShape.CIRCLE,
        expand=True,
        bgcolor="white",
        animate_scale=ft.animation.Animation(175, ft.AnimationCurve.BOUNCE_IN_OUT),
        height=132,
        width=132,
        alignment=ft.alignment.center
    )
    stack_say = ft.Stack(controls=[circle_say3, circle_say1, circle_say2], alignment=ft.alignment.center)
    voice_button = ft.IconButton(
        icon=ft.icons.MIC,
        icon_color="#186694",
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
        bgcolor=ft.colors.with_opacity(0.5, ft.colors.WHITE),
    )
    voice_stack = ft.Stack(
        controls=[animated_background, voice_container],
        alignment=ft.alignment.center,
    )

    switch = ft.AnimatedSwitcher(
        voice_stack,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=200,
        reverse_duration=100,
        switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
        switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
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
        content=switch,
        alignment=ft.alignment.center,
        padding=50
    )

    gradient_container = ft.Container(
        content=ft.Column(
            [image_container, chat_container, bottom_container],
            tight=True,
            spacing=5,
        ),
        gradient=gradient,
        expand=True,
    )

    page.add(gradient_container)

ft.app(target=main)
