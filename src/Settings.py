# Utilities
from dotenv import load_dotenv
import os
import pymupdf

# AI
import openai
import chromadb

def init_environment():
    load_dotenv()
    # Settings
    global maxConcurrentApiRequests
    maxConcurrentApiRequests = 3
    global llmBaseUrl
    llmBaseUrl = "https://api.deepseek.com"
    global llmModel
    llmModel= "deepseek-reasoner"
    global ocrBaseUrl
    ocrBaseUrl= "https://api.clarifai.com/v2/ext/openai/v1"
    global ocrModel
    ocrModel= "https://clarifai.com/deepseek-ai/deepseek-ocr/models/DeepSeek-OCR"
    # DeepSeek-OCR (Clarifai)
    # TODO: use platform.deepseek.com when deepseek-ocr is available there
    global ocrLLMClient
    ocrLLMClient = openai.AsyncOpenAI(
        base_url=ocrBaseUrl,
        api_key=os.getenv("OCR_API_KEY"),
    )
    # DeepSeek-LLM (DeepSeek Platform)
    global genericLLMClient
    genericLLMClient = openai.AsyncOpenAI(
        base_url=llmBaseUrl,
        api_key=os.getenv("LLM_API_KEY"),
    )
    # Other variables
    global pixmapScale
    pixmapScale = pymupdf.Matrix(2.5, 2.5)
    global ragClient
    ragClient = chromadb.PersistentClient(path="./db")
    global ragDb
    ragDb = ragClient.get_or_create_collection(name="questionsDatabase")
    global ragNResults
    ragNResults = 3

class Debugger:
    @staticmethod
    def printList(elements, tag):
        print(f"[DEBUG] <{tag}> started.")
        for index in range(len(elements)):
            print(f"<=== #{index + 1} ===>")
            print(elements[index])
        print(f"[DEBUG] <{tag}> finished!\n")
