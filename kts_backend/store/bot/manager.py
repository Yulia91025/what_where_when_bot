import time
import typing
from logging import getLogger


from kts_backend.store.vk_api.dataclasses import Message, Update, UpdateObject

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class GameState:
    def __init__(self, chat_id, captain_id, bot: "BotManager"):
        self.chat_id = chat_id
        self.captain_id = captain_id
        self.bot = bot

        self.points = 0
        self.round_num = 0
        self.round_resp = dict()
        self.time = None
        self.start_timer = False

        self.start = self._create_start
        self.question = self._create_question
        self.timer = self._create_timer
        self.choose_resp = self._create_respondent
        self.response = self._create_response
        self.final = self._create_final       

        self.current_state = self.start 


    async def send(self, update):
        try:
            if self.time is not None and not self.start_timer:
                self.start_timer = True
                await self.current_state(update)
            elif not self.start_timer:
                await self.current_state(update)
            return False
        except:
            return True


    async def _create_start(self, update): 
        self.players = await self.bot.app.store.game.get_players(self.chat_id)
        captain_id = int(update.object.user_id)
        for player in self.players:
            if captain_id == player.vk_id:
                captain_name = player.name
                break
        await self.new_message(update, f"Капитан [id{captain_id}|{captain_name}]")
        self.current_state = self.question


    async def _create_question(self, update):
        if "Промежуточные результаты" in update.object.text:
            await self.new_message(update, f"Количество очков знатоков : {self.points} %0A Количество очков телезрителей : {len(self.round_resp) - self.points}", "Следующий вопрос")
        else:
            self.round_num += 1
            await self.new_message(update, "*Вопрос* %0A На размышление даётся 1 минута")

            self.time = time.time()
            self.current_state = self.timer
            self.bot.timer_flag = True


    async def _create_timer(self, update):
        while True:                
            if time.time() - self.time >= 10.0:
                await self.new_message(update, "Время вышло! Капитан, введите id отвечающего")
                break
        self.time = None
        self.start_timer = False
        self.current_state = self.choose_resp 


    async def _create_respondent(self, update):
        if update.object.user_id == self.captain_id:
            string = update.object.text.rsplit("id")
            player_id = int(string[1][:9])
            for player in self.players:
                if player.vk_id == player_id:
                    self.round_resp[self.round_num] = player_id
                    await self.new_message(update, f"Oтвечает [id{player_id}|{player.name}]") 
                    self.current_state = self.response       

    async def _create_response(self, update):
        if int(update.object.user_id) == int(self.round_resp[self.round_num]):
            if self.points == 6 or len(self.round_resp) - self.points == 6:                 
                self.current_state = self.final
                keyboard = {
                    "inline": True,
                    "one_time": False,
                    "buttons": [
                        [
                            {"action": {"type": "text", "label": "Подвести итоги"}},
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
                            {"action": {"type": "text", "label": "Промежуточные результаты"}},
                            {"action": {"type": "text", "label": "Следующий вопрос"}},
                        ]
                    ],
                }  

            if "*правильный ответ*" in update.object.text:
                self.points += 1
                await self.new_message(update, "Верно! У вас +1 очко", None, keyboard)
            else:
                await self.new_message(update, "Неверно", None, keyboard)
     


    async def _create_final(self, update):
        # выводит итоги 
        await self.new_message(update, f"Итоги: {self.points}")
        raise Exception
    
    async def new_message(self, update: Update, text: str, keyboard_text = None, keyboard = None):   
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
                keyboard=keyboard
            )
        )    


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

        self.current_game_states = []
        self.timer_flag = False

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
                game = await self.app.store.game.create_game(chat_id=chat_id, users=users)
                game_state = GameState(chat_id=chat_id, captain_id=captain_id, bot=self)
                await game_state.send(update)
                await game_state.send(update)
                self.current_game_states.append(game_state)
            elif str(self.app.config.bot.group_id) in update.object.text:
                keyboard = {
                    "inline": True,
                    "one_time": False,
                    "buttons": [
                        [
                            {"action": {"type": "text", "label": "Начнём игру!"}},
                        ]
                    ],
                }
                await self.app.store.messages_queue.put(
                    Message(
                        user_id=update.object.user_id,
                        text="Привет! Я бот-ведущий игры Что? Где? Когда? %0A Первый, кто  нажмёт кнопку 'Начать игру!' будет объявлен капитаном команды знатоков.",
                        peer_id=update.object.peer_id,
                        keyboard=keyboard
                    )
                )            

    def get_game_state(self, chat_id):
        for game_state in self.current_game_states:
            if game_state.chat_id == chat_id:
                return game_state
        return None   







