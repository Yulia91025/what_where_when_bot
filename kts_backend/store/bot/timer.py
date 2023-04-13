import time
import random
import asyncio
from asyncio import Task
from typing import Optional

from kts_backend.store.bot.manager import GameState


class Timer:
    def __init__(self, gamestate: GameState, round_num: int):
        self.gamestate = gamestate
        self.is_running = False
        self.round = round_num
        self.task: Optional[Task] = None

    async def start(self, update, t1_or_t2):
        self.is_running = True
        if t1_or_t2 == 1:
            self.task = asyncio.create_task(self.t1(update))
        elif t1_or_t2 == 2:
            self.task = asyncio.create_task(self.t2(update))

    async def stop(self):
        self.is_running = False
        await self.task.cancel()

    async def t1(self, update):
        self.is_running = await self.t(60)
        if (
            self.gamestate.current_state == self.gamestate.timer
            and not self.is_running
            and self.round == self.gamestate.round_num
        ):
            self.gamestate.current_state = self.gamestate.choose_resp
            await self.gamestate.new_message(
                update,
                f"Время вышло! [id{self.gamestate.captain_id}|Капитан], укажите на отвечающего (через @)",
            )

    async def t2(self, update):
        self.is_running = await self.t(120)
        if (
            (
                self.gamestate.current_state == self.gamestate.choose_resp
                or self.gamestate.current_state == self.gamestate.response
            )
            and not self.is_running
            and self.round == self.gamestate.round_num
        ):
            await self.checking(update)

    async def t(self, sec: int):
        await asyncio.sleep(sec)
        return False

    async def checking(self, update):
        Enter = "%0A"

        correct_answers = self.gamestate.current_question.answers
        correct_answers_titles = []
        for corr_ans in correct_answers:
            correct_answers_titles.append(corr_ans.title)

        if self.gamestate.round_num - self.gamestate.points == 5:
            self.gamestate.current_state = self.gamestate.final
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
            self.gamestate.current_state = self.gamestate.question
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

        corr_ans = correct_answers_titles[0]
        string = (
            "Время вышло! Вы ничего не ответили, поэтому очко уходит телезрителям."
            + Enter
            + "Правильный ответ: "
            + corr_ans.capitalize()
        )
        if len(correct_answers_titles) > 1:
            string += Enter + "Так же засчитывались ответы: "
            for i in range(1, len(correct_answers_titles)):
                string += Enter + correct_answers_titles[i].capitalize()

        indx_attachment = random.randint(
            0, len(self.gamestate.player_lost_attachments) - 1
        )
        attachment = self.gamestate.player_lost_attachments[indx_attachment]
        await self.gamestate.new_message(
            update, string, None, keyboard, attachment
        )

        self.gamestate.round_num += 1

        if self.gamestate.round_num < 11:
            self.gamestate.current_question = self.gamestate.game.questions[
                self.gamestate.round_num
            ]
