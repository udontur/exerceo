import os

# Utilities
from dotenv import load_dotenv
import pymupdf
import asyncio
import base64
# import time

# AI Stuff
import openai


def init_environment():
    load_dotenv()
    # DeepSeek-OCR (Clarifai)
    global ocrLLMClient
    ocrLLMClient = openai.AsyncOpenAI(
        base_url=os.getenv("OCR_BASE_URL"),
        api_key=os.getenv("OCR_API_KEY"),
    )
    # DeepSeek-LLM (DeepSeek Platform)
    global genericLLMClient
    genericLLMClient = openai.AsyncOpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
    )
    global pixmapScale
    pixmapScale = pymupdf.Matrix(2.5, 2.5)


class Converter:
    @staticmethod
    # Turns pdf into a JPEG list
    def pdfToImages(pdfFilePath):
        pdfBinary = open(pdfFilePath, "rb").read()
        pdfDocument = pymupdf.open(
            stream=pdfBinary,
            filetype="pdf",
        )

        imageList = []
        for pdfPage in pdfDocument:
            currentPixmap = pdfPage.get_pixmap(matrix=pixmapScale)
            currentImage = currentPixmap.pil_tobytes("JPEG")
            imageList.append(currentImage)
        pdfDocument.close()
        return imageList

    def flattenList(nestedList):
        flattenedList = []
        for subList in nestedList:
            # The split is only specific to the PDF parser
            flattenedList.extend(subList.split("\n\n"))
        return flattenedList

    # Bundle k elements in the array
    def kBundle(elements, k):
        result = []
        index = 0
        while index < len(elements):
            currentElement = ""
            for i in range(index, index + k):
                if i >= len(elements):
                    break
                currentElement += elements[i]
            result.append(currentElement)
            index += k
        return result

    # TODO: add a rate limit for the coros
    async def extractRawLatex(rawLatexList):
        coros = []
        for latexBundle in rawLatexList:
            coro = LLMs.rawLatexToParsedLatex(rawLatex=latexBundle)
            coros.append(coro)
        return await asyncio.gather(*coros)

    # Turns a image list into Latex, maps individual image to a list
    async def imagesToLatex(imageList):
        coros = []

        for image in imageList:
            coro = await LLMs.imageToLatex(imageBytes=image)
            coros.append(coro)
            # time.sleep(1.1)

        # TODO: Temporary as it can only process 1 API request per second
        # return await asyncio.gather(*coros)
        return coros


class Debugger:
    @staticmethod
    def printList(elements, tag):
        print(f"[DEBUG] <{tag}> started.")
        for index in range(len(elements)):
            print(f"<=== #{index + 1} ===>")
            print(elements[index])
        print(f"[DEBUG] <{tag}> finished!\n")


class LLMs:
    @staticmethod
    async def promptResponse(prompt, llmModel, llmClient):
        # DEBUG_PRINT
        print(f"[DEBUG] Calling {llmModel}")
        response = await llmClient.chat.completions.create(
            model=os.getenv(llmModel), messages=prompt
        )
        print("[DEBUG] SUCCESSFUL\n")
        return response.choices[0].message.content

    async def rawLatexToParsedLatex(rawLatex):
        questionExtractionPrompt = """
        **Objective**: Extract and structure individual questions from practice/exam papers while preserving original formatting and grouping related multi-part questions.

        **Input Processing Rules**:
        - Extract ONLY question text and associated sub-questions.
        - Remove: Instructions, headings, page numbers, section titles, author information, copyright notices, and other contextual metadata.
        - Preserve mathematical expressions, LaTeX formatting, and special symbols exactly as written.
        - Treat sub-questions (e.g. part a and part b) as the same question as the main question.

        **Output Rules**:
        - Separate each complete question (including all sub-parts) with exactly two newline characters (`\n\n`).

        **Input Text to Parse**:
        """
        prompt = [
            {"role": "system", "content": questionExtractionPrompt},
            {"role": "user", "content": rawLatex},
        ]
        return await LLMs.promptResponse(
            prompt=prompt,
            llmModel="LLM_MODEL",
            llmClient=genericLLMClient,
        )

    # TODO: replace with deepseek-ocr when it is available on platforms.deepseek.com
    async def imageToLatex(imageBytes):
        imageBase64 = base64.b64encode(imageBytes).decode()
        prompt = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text and tables in LaTeX format.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{imageBase64}"},
                    },
                ],
            }
        ]
        return await LLMs.promptResponse(
            prompt=prompt,
            llmModel="OCR_MODEL",
            llmClient=ocrLLMClient,
        )


async def pdfParser(filePath):
    pdfImageList = Converter.pdfToImages(filePath)
    rawLatexList = await Converter.imagesToLatex(pdfImageList)

    rawLatexListBundle = Converter.kBundle(rawLatexList, 3)  # >5 is very inaccurate
    # DEBUG_PRINT
    # Debugger.printList(rawLatexListBundle, "Raw Latex List Bundled")

    parsedLatexList = await Converter.extractRawLatex(rawLatexListBundle)
    # DEBUG_PRINT
    # Debugger.printList(parsedLatexList, "Parsed Latex List")

    parsedQuestions = Converter.flattenList(parsedLatexList)
    # DEBUG_PRINT
    # Debugger.printList(parsedQuestions, "Parsed Questions")

    return parsedQuestions

    # TODO: seperate them into seperate files


async def main():
    parsedQuestions = await pdfParser("./assets/test/latex-test-1.pdf")
    Debugger.printList(parsedQuestions, "Parsed Questions")


if __name__ == "__main__":
    init_environment()
    asyncio.run(main())

# Parse JSON -> a list -> vector embedding
# Make this a API backend and connect to MGL's front end
# Docker and kubernets
