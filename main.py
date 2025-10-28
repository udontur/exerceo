import os

# Utilities
from dotenv import load_dotenv
import pymupdf
import json

# AI Stuff
from clarifai.client.model import Model
from openai import OpenAI

def init_environment():
    load_dotenv()
    global nougatEngine
    nougatEngine = Model(
        url=os.getenv("NOUGAT_API_KEY"),
        pat=os.getenv("NOUGAT_API_BASE"),
    )
    client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_API_BASE"),
    )

class Converter:
    @staticmethod
    # Turns pdf into a JPEG list
    def pdfToImage(pdfFilePath):
        pdfBinary = open(pdfFilePath, "rb").read()
        pdfDocument = pymupdf.open(
            stream=pdfBinary,
            filetype="pdf",
        )
        pixmapScale = pymupdf.Matrix(2.5, 2.5)
        imageList = []
        for pdfPage in pdfDocument:
            currentPixmap = pdfPage.get_pixmap(matrix=pixmapScale)
            currentImage = currentPixmap.pil_tobytes("JPEG")
            imageList.append(currentImage)
        pdfDocument.close()
        return imageList
    # Turns a image list into Latex, maps individual image to a list
    def imageToLatex(imageList):
        latexPage = []
        for image in imageList:
            nougatOcrResult = nougatEngine.predict_by_bytes(
                input_bytes=image,
                input_type="image",
            )
            latexPage.append(nougatOcrResult.outputs[0].data.text.raw)
        return latexPage

class Debugger:
    @staticmethod
    def printList(elements, tag):
        print(f"[DEBUG] <{tag}> started.")
        for index in range(len(elements)):
            print(f"<=== #{index}+1 ===>")
            print(elements[index])
        print(f"[DEBUG] <{tag}> finished!")

class LLMs:
    def promptResponse(systemPrompt, userPrompt):
        prompt = [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ]

        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=prompt,
            response_format={
                "type": "json_object"
            }
        )

        print(json.loads(response.choices[0].message.content))

# The model will init --> very very very slow
# Extract questions using DeepSeek for every 5 page as a bundle
# JSON Output for each question, including subquestions: https://api-docs.deepseek.com/guides/json_mode
# Parse JSON -> a list -> vector embedding 

def main():
    filePath = "./assets/test/latex-test-1page.pdf"
    pdfImageList = Converter.pdfToImage(filePath)
    rawLatexList = Converter.imageToLatex(pdfImageList)
    Debugger.printList(rawLatexList, "Unparsed Latex List")


if __name__ == "__main__":
    init_environment()
    main()
