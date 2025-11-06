# Utilities
from dotenv import load_dotenv
import os
import pymupdf

# AI
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


class Debugger:
    @staticmethod
    def printList(elements, tag):
        print(f"[DEBUG] <{tag}> started.")
        for index in range(len(elements)):
            print(f"<=== #{index + 1} ===>")
            print(elements[index])
        print(f"[DEBUG] <{tag}> finished!\n")
