import random
import typing
from logging import getLogger


from kts_backend.store.vk_api.dataclasses import Message, Update, UpdateObject
from kts_backend.store.models.models import Game


if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application

Enter = "%0A"


class GameState:
    def __init__(
        self, game: Game, chat_id: int, captain_id: int, bot: "BotManager"
    ):
        self.game = game
        self.chat_id = chat_id
        self.captain_id = captain_id
        self.bot = bot

        self.points = 0
        self.round_num = 0
        self.round_resp = dict()
        self.current_question = self.game.questions[0]

        self.player_win_attachments = [
            "doc370512811_626810933",
            "doc146519153_618688387",
            "doc12356819_599724021",
            "doc445215334_575602109",
            "doc138266642_604261251",
            "doc1839095_542216537",
        ]
        self.player_lost_attachments = [
            "doc159273518_624854260",
            "doc577953304_663068266",
            "doc288439887_502139874",
            "doc130496292_577271566",
        ]

        self.start = self._create_start
        self.question = self._create_question
        self.timer = self._create_timer
        self.choose_resp = self._create_respondent
        self.response = self._create_response
        self.final = self._create_final

        self.current_state = self.start

    async def send(self, update):
        try:
            await self.current_state(update)
            return False
        except:
            return True

    async def _create_start(self, update):
        self.players = self.game.players
        captain_id = int(update.object.user_id)
        for player in self.players:
            if captain_id == player.vk_id:
                captain_name = player.name
                break
        await self.new_message(
            update, f"Капитан [id{captain_id}|{captain_name}]"
        )
        self.current_state = self.question

    async def _create_question(self, update):
        if "Промежуточные результаты" in update.object.text:
            points = await self.bot.app.store.game.get_current_game_points(
                self.game.id
            )
            string = "Количество очков знатоков : " + str(points) + Enter
            string += "Количество очков телезрителей : " + str(
                self.round_num - points
            )
            await self.new_message(update, string, "Следующий вопрос")
        elif (
            "Начнём игру!" in update.object.text
            or "Следующий вопрос" in update.object.text
        ):
            question = self.current_question
            string = "Раунд " + str(self.round_num + 1) + Enter + Enter
            string += (
                question.title
                + Enter
                + Enter
                + "На размышление даётся 1 минута."
            )

            self.current_state = self.timer

            await self.new_message(update, string, "Ответить раньше")

    async def _create_timer(self, update):
        if "Ответить раньше" in update.object.text:
            self.current_state = self.choose_resp
            await self.new_message(
                update,
                f"[id{self.captain_id}|Капитан], укажите на отвечающего (через @)",
            )

    async def _create_respondent(self, update):
        if update.object.user_id == self.captain_id:
            if "id" in update.object.text:
                string = update.object.text.rsplit("id")
                player_id = int(string[1][:9])
                for player in self.players:
                    if player.vk_id == player_id:
                        self.round_resp[self.round_num] = player_id
                        await self.new_message(
                            update, f"Oтвечает [id{player_id}|{player.name}]"
                        )
                        self.current_state = self.response

    async def _create_response(self, update):
        if int(update.object.user_id) == int(self.round_resp[self.round_num]):

            comments = self.current_question.comments
            correct_answers = self.current_question.answers
            correct_answers_titles = []
            for corr_ans in correct_answers:
                correct_answers_titles.append(corr_ans.title)

            is_correct = False
            for ans in correct_answers_titles:
                ans_beauty = ans.lower()
                ans_beauty = ans_beauty.replace(".", "")
                ans_beauty = ans_beauty.lstrip()
                ans_beauty = ans_beauty.rstrip()
                if ans_beauty in update.object.text.lower():
                    is_correct = True
                    break

            if (self.points == 5 and is_correct) or (
                self.round_num - self.points == 5 and not is_correct
            ):
                self.current_state = self.final
                keyboard = {
                    "inline": True,
                    "one_time": False,
                    "buttons": [
                        [
                            {
                                "action": {
                                    "type": "text",
                                    "label": "Подвести итоги",
                                }
                            },
                        ]
                    ],
                }
            else:
                self.current_state = self.question
                keyboard = {
                    "inline": True,
                    "one_time": False,
                    "buttons": [
                        [
                            {
                                "action": {
                                    "type": "text",
                                    "label": "Промежуточные результаты",
                                }
                            },
                            {
                                "action": {
                                    "type": "text",
                                    "label": "Следующий вопрос",
                                }
                            },
                        ]
                    ],
                }

            if is_correct:
                self.points += 1
                indx_attachment = random.randint(
                    0, len(self.player_win_attachments) - 1
                )
                attachment = self.player_win_attachments[indx_attachment]
                string = "Верно! У вас плюс 1 очко!"
                if comments is not None and not comments.isspace():
                    string += (
                        Enter
                        + Enter
                        + "Комментарий к ответу: "
                        + comments.capitalize()
                    )
                await self.bot.app.store.game.inc_game_points(self.game.id)
                await self.new_message(
                    update,
                    string,
                    None,
                    keyboard,
                    attachment,
                )
            else:
                corr_ans = correct_answers_titles[0]
                indx_attachment = random.randint(
                    0, len(self.player_lost_attachments) - 1
                )
                attachment = self.player_lost_attachments[indx_attachment]
                string = (
                    "Неверно"
                    + Enter
                    + "Правильный ответ: "
                    + corr_ans.capitalize()
                )
                if len(correct_answers_titles) > 1:
                    string += Enter + "Так же засчитывались ответы: "
                    for i in range(1, len(correct_answers_titles)):
                        string += Enter + correct_answers_titles[i].capitalize()
                if comments is not None and not comments.isspace():
                    string += (
                        Enter
                        + Enter
                        + "Комментарий к ответу: "
                        + comments.capitalize()
                    )
                await self.new_message(
                    update, string, None, keyboard, attachment
                )

            self.round_num += 1

            if self.round_num < 11:
                self.current_question = self.game.questions[self.round_num]

    async def _create_final(self, update):
        if "Подвести итоги" in update.object.text:
            players_points = (
                await self.bot.app.store.game.get_current_game_points(
                    self.game.id
                )
            )
            bot_points = self.round_num - players_points
            string = (
                "Итоги игры: "
                + Enter
                + Enter
                + "Количество раундов: "
                + str(self.round_num)
                + Enter
            )
            string += (
                "Количество очков знатоков: " + str(players_points) + Enter
            )
            string += (
                "Количество очков телезрителей: "
                + str(bot_points)
                + Enter
                + Enter
            )
            if players_points > bot_points:
                attachment = "photo-218813853_457239227"
                string += "Поздравляю! Победа знатоков! :)"
            else:
                attachment = "photo-218813853_457239228"
                string += "Победила команда телезрителей :("
            await self.new_message(update, string, attachment=attachment)
            raise Exception

    async def new_message(
        self,
        update: Update,
        text: str,
        keyboard_text=None,
        keyboard=None,
        attachment=None,
    ):
        if keyboard_text is not None:
            keyboard = {
                "inline": True,
                "one_time": False,
                "buttons": [
                    [
                        {"action": {"type": "text", "label": keyboard_text}},
                    ]
                ],
            }
        await self.bot.app.store.messages_queue.put(
            Message(
                user_id=update.object.user_id,
                text=text,
                peer_id=update.object.peer_id,
                keyboard=keyboard,
                attachment=attachment,
            )
        )

        from kts_backend.store.bot.timer import Timer

        if "На размышление даётся 1 минута" in text:
            self.t = Timer(self, self.round_num)
            await self.t.start(update, 1)

        if "укажите на отвечающего (через @)" in text:
            self.t = Timer(self, self.round_num)
            await self.t.start(update, 2)


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

        self.current_game_states = []

        self.logger = getLogger("handler")

    async def handle_updates(self, update: Update):
        if update.type == "message_new":
            chat_id = update.object.peer_id
            game_state = self.get_game_state(chat_id)
            if game_state is not None:
                is_end = await game_state.send(update)
                if is_end:
                    self.current_game_states.remove(game_state)
            elif "Начнём игру!" in update.object.text:
                captain_id = update.object.user_id
                users = await self.app.store.vk_api._get_members(chat_id)
                try:
                    game = await self.app.store.game.create_game(
                        chat_id=chat_id, users=users
                    )
                    game_state = GameState(
                        game=game,
                        chat_id=chat_id,
                        captain_id=captain_id,
                        bot=self,
                    )
                    await game_state.send(update)
                    await game_state.send(update)
                    self.current_game_states.append(game_state)
                except:
                    text = "Извините, пока в базе данных недостаточно вопросов для начала игры :("
                    await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,
                            peer_id=update.object.peer_id,
                        )
                    )
            elif str(self.app.config.bot.group_id) in update.object.text:
                keyboard = {
                    "inline": True,
                    "one_time": False,
                    "buttons": [
                        [
                            {
                                "action": {
                                    "type": "text",
                                    "label": "Начнём игру!",
                                }
                            },
                        ]
                    ],
                }
                text = (
                    "Привет!" + Enter + 'Я бот-ведущий игры "Что? Где? Когда?"'
                )
                text += (
                    Enter
                    + Enter
                    + 'Первый, кто  нажмёт кнопку "Начнём игру!", будет объявлен капитаном команды знатоков.'
                )
                await self.app.store.messages_queue.put(
                    Message(
                        user_id=update.object.user_id,
                        text=text,
                        peer_id=update.object.peer_id,
                        keyboard=keyboard,
                        attachment="doc151911296_516026762",
                    )
                )
        # else:
        #     await self.app.store.messages_queue.put(0)

    def get_game_state(self, chat_id) -> GameState:
        for game_state in self.current_game_states:
            if game_state.chat_id == chat_id:
                return game_state
        return None
