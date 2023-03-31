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
                for url in urls:
                    full_url = main_url + url
                    questions, answers = await self.parse_questions(full_url)
                    for i in range(len(questions)):
                        try:
                            all_questions.append(questions[i])
                            all_answers.append(answers[i])
                        except:
                            pass
                return all_questions, all_answers

    async def parse_questions(self, url: str):
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url) as response:
                page = await response.text()
                soup = BeautifulSoup(page, "html.parser")

                questions_str = []
                allp = soup.findAll("p")
                for data in allp:
                    if data.find("strong", class_="Question") is not None:
                        questions_str.append(data.text)

                answers_str = []
                for data in allp:
                    if data.find("strong", class_="Answer") is not None:
                        answers_str.append(data.text)

                questions = []
                answers = []
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
                        ):
                            questions.append(question)
                            answers.append(answers_str[i].rsplit(": ")[1])
                    except:
                        if len(questions) > len(answers):
                            questions.pop()
                return questions, answers
