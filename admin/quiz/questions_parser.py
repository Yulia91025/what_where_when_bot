from bs4 import BeautifulSoup

import aiohttp


class QuestionParser:
    async def parse_main(self):
        main_url = "https://db.chgk.info"
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(main_url) as response:
                page = await response.text()
                soup = BeautifulSoup(page, "html.parser")

                all_urls = []
                alla = soup.findAll("a")
                for link in alla:
                    all_urls.append(link.get("href"))
                urls = []
                for url in all_urls:
                    if "/tour/" in url:
                        urls.append(url)
                all_questions = []
                all_answers = []
                all_comments = []
                for url in urls:
                    full_url = main_url + url
                    questions, answers, comments = await self.parse_questions(
                        full_url
                    )
                    for i in range(len(questions)):
                        try:
                            all_questions.append(questions[i])
                            all_answers.append(answers[i])
                            all_comments.append(comments[i])
                        except:
                            raise IndexError

                return all_questions, all_answers, all_comments

    async def parse_questions(self, url: str):
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url) as response:
                page = await response.text()
                soup = BeautifulSoup(page, "html.parser")

                questions_str = []
                answers_str = []
                comments_str = []
                indx = 0
                allp = soup.findAll("p")
                for data in allp:
                    if data.find("strong", class_="Question") is not None:
                        questions_str.append(data.text)
                        indx += 1
                    elif data.find("strong", class_="Answer") is not None:
                        answers_str.append(data.text)
                        indx += 1
                    elif data.find("strong", class_="Comments") is not None:
                        if len(questions_str) == len(comments_str):
                            comments_str.pop()
                        comments_str.append(data.text)
                        indx += 1
                    elif (indx + 1) % 3 == 0:
                        comments_str.append(": ")
                        indx += 1

                questions = []
                answers = []
                comments = []
                for i, question_str in enumerate(questions_str):
                    try:
                        question = question_str.rsplit(": ")[1]
                        if not (
                            "блиц" in question.lower()
                            or "дуплет" in question.lower()
                            or "раздаточный материал" in question.lower()
                            or "на раздаточном материале" in question.lower()
                            or "картинка" in question.lower()
                            or "фото" in question.lower()
                            or "на картинке" in question.lower()
                            or "на фото" in question.lower()
                            or "перед вами" in question.lower()
                            or "qr-код" in question.lower()
                            or "внимание" in question.lower()
                            or "ведущему" in question.lower()
                            or "редактор" in question.lower()
                            or "вопрос" in question.lower()
                        ):
                            questions.append(question)
                            answers.append(answers_str[i].rsplit(": ")[1])
                            comments.append(comments_str[i].rsplit(": ")[1])
                    except:
                        if len(questions) > len(answers):
                            questions.pop()
                        if len(questions) > len(comments):
                            comments.append(None)
                return questions, answers, comments
