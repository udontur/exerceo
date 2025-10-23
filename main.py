import os
from dotenv import load_dotenv
from clarifai.client.model import Model
import pymupdf

load_dotenv()
nougatEngine = Model(
    url="https://clarifai.com/facebook/nougat/models/nougat-base",
    pat=os.getenv("NOUGAT_API"),
)

pixmapScale = pymupdf.Matrix(2.5, 2.5)


def pdfToRawLatex(pdfFilePath):
    pdfBinary = open(pdfFilePath, "rb").read()
    pdfDocument = pymupdf.open(
        stream=pdfBinary,
        filetype="pdf",
    )
    rawLatex = []
    for pdfPage in pdfDocument:
        # print(f"<=== #{pdfPage.number + 1} ===>")
        currentPixmap = pdfPage.get_pixmap(matrix=pixmapScale)
        # currentPixmap.save("image.jpeg")
        currentImage = currentPixmap.pil_tobytes("JPEG")
        nougatOcrResult = nougatEngine.predict_by_bytes(
            input_bytes=currentImage,
            input_type="image",
        )
        rawLatex.append(nougatOcrResult.outputs[0].data.text.raw)
        # print(nougatOcrResult.outputs[0].data.text.raw)

    pdfDocument.close()
    return rawLatex


# Extract questions using DeepSeek for every 5 page as a bundle
# JSON Output for each question, including subquestions: https://api-docs.deepseek.com/guides/json_mode
# Python formatting
# Better package managment


def main():
    filePath = "./assets/test/latex-test-1page.pdf"
    rawLatex = pdfToRawLatex(filePath)
    for index in range(len(rawLatex)):
        print(f"<=== #{index} ===>")
        print(rawLatex[index])


if __name__ == "__main__":
    main()
