import os

# Utilities
from dotenv import load_dotenv
import pymupdf
import json
import asyncio

# AI Stuff
from clarifai.client.model import Model
from openai import AsyncOpenAI

def init_environment():
    load_dotenv()
    global nougatEngine
    nougatEngine = Model(
        url=os.getenv("NOUGAT_API_BASE"),
        pat=os.getenv("NOUGAT_API_KEY"),
    )
    global genericLLMClient
    genericLLMClient = AsyncOpenAI(
        base_url=os.getenv("LLM_API_BASE"),
        api_key=os.getenv("LLM_API_KEY"),
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
            print("CALLING CLARIFAI")
            nougatOcrResult = nougatEngine.predict_by_bytes(
                input_bytes=image,
                input_type="image",
            )
            print("SUCCESSFUL")
            latexPage.append(nougatOcrResult.outputs[0].data.text.raw)
        return latexPage
    # Bundle 5 elements in the array
    def kBundle(elements, k):
        result = []
        index = 0
        while index<len(elements):
            currentElement=""
            for i in range(index, index+k):
                if i>=len(elements):
                    break
                currentElement+=elements[i]
            result.append(currentElement)
            index+=k
        return result
            

class Debugger:
    @staticmethod
    def printList(elements, tag):
        print(f"[DEBUG] <{tag}> started.")
        for index in range(len(elements)):
            print(f"<=== #{index+1} ===>")
            print(elements[index])
        print(f"[DEBUG] <{tag}> finished!")

class LLMs:
    questionExtractPrompt = """
        Given a large paragraph of text, parse and extract each question and return each question as the sampled JSON format. The input text is large and may contain elements that are not part of a question, ignore those elements. If a question has two parts, treat them as one question. 
        
        EXAMPLE JSON OUOTPUT:
        {
            "Questions": [
                "What is 1+1?",
                "How do create an SSH key?",
                "What is the vertical asymptote of the function f(x)=(x-2)/(x^2+3x+2)"
            ]
        }
        
        Parse the following text:
    """
    @staticmethod
   
    async def promptResponse(systemPrompt, userPrompt):
        prompt = [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ]
        print("CALLING DEEPSEEK")
        response = await genericLLMClient.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=prompt,
            response_format={
                "type": "json_object"
            }
        )
        print("SUCCESSFUL")
        # This is a JSON formatted string
        return response.choices[0].message.content

async def extractRawLatex(rawLatexList):
    parsedLatexJsonList = []
    coros = []
    for latexBundle in rawLatexList:
        coro=LLMs.promptResponse(
            systemPrompt=LLMs.questionExtractPrompt,
            userPrompt=latexBundle
        )
        coros.append(coro)
        
    parsedLatexJsonList = await asyncio.gather(*coros)
    return parsedLatexJsonList

async def main():
    filePath = "./assets/test/latex-test-1.pdf"
    pdfImageList = Converter.pdfToImage(filePath)
    rawLatexList = Converter.imageToLatex(pdfImageList)

    # rawLatexList=['\n\n# WAH YAN COLLEGE, HONG KONG\n\nMATHEMATICS Extended Part\n\nModule 2 (Algebra and Calculus)\n\nForm 6 Mock Exam\n\nDate: 15/1/2024\n\n8:15 am - 10:45 am (2.5 hours)\n\nThis paper must be answered in English\n\n###### Abstract\n\nInstructions\n\n1. After the announcement of the start of the examination, you should first write down your Name, Class and Class Number in the spaces provided on Page 1.\n2. This paper consists of TWO sections, A and B.\n3. Attempt ALL questions in this paper. Write your answers in the spaces provided in this Question-Answer Book.\n4. Supplementary answer sheets will be supplied on request. Write your Name, Class and Class Number on each sheet.\n5. Unless otherwise specified, all working must be clearly shown.\n6. Unless otherwise specified, numerical answers must be exact.\n\nThis exam paper contains 32 pages (including this cover page) and 12 questions.\n\nTotal of marks is 100.\n\n', '\n\n[MISSING_PAGE_POST]\n\n ', '3. Let \\(n\\) be an integer greater than 1. Define \\((x-a)^{n}=\\sum\\limits_{k=0}^{n}\\mu_{k}x^{k}\\), where \\(a\\) is an integral constant. It is given that \\(\\frac{p_{2}}{\\mu_{1}}=-\\frac{4}{3}\\). 1. Chungclung claims that \\(n\\) is an odd number and \\(a>0\\). Do you agree? Explain your answer. 2. Let \\((bx-6)^{2n}=\\frac{\\sum\\limits_{k=0}^{n}}{\\lambda_{k}x^{2n-k}}\\), where \\(b\\) is an integral constant. If \\(\\lambda_{b}=\\mu_{n}\\) and \\(\\lambda_{b}=-4\\mu_{n-1}\\), find \\(a,b\\) and \\(n\\). (5 marks) ', '4. (a) Prove that \\(\\sin\\pi x^{2}+\\sin 2\\pi x-\\sin\\pi\\left(x^{2}+2x\\right)=4\\sin\\frac{\\pi\\left(x^{2}+2x \\right)}{2}\\sin\\frac{\\pi x^{2}}{2}\\sin\\pi x\\). (b) Find the least positive value of \\(x\\) such that \\(\\sin\\pi x^{2}+\\sin 2\\pi x=\\sin\\pi\\left(x^{2}+2x\\right)\\). (6 marks) ', '', '5. Consider the curve \\(\\Gamma:g=e^{-2k}\\), where \\(x\\geq 0\\). Let \\(P\\) be a moving point on \\(\\Gamma\\) with \\(k\\) as its \\(x-\\)coordinate, where \\(h>0\\). Denote the tangent to \\(\\Gamma\\) at \\(P\\) by \\(L\\) and the area of the region bounded by \\(\\Gamma,L\\) and the \\(p\\)-axis by \\(A\\). 1. [label=()] 2. Prove that \\(A=\\frac{e^{-2k}\\left(e^{2k}-2h-1\\right)}{2}\\). 3. If \\(h=\\ln(t+1)\\), where \\(t\\) is the time, find the rate of change of \\(A\\) when \\(t=2\\). (7 marks) \\(\\blacksquare\\) ', '* 6. (a) Find \\(\\int\\frac{x+\\sin x}{1+\\cos x}\\mathrm{d}x\\). (b) At any point \\((x,y)\\) on the curve \\(\\Gamma\\), the slope of the tangent to \\(\\Gamma\\) is \\(\\frac{1+x-\\cos x+\\sin x}{1+\\cos x}\\). Given that \\(\\Gamma\\) passes through the point \\(\\left(\\frac{x}{1},2+\\pi\\right)\\), does \\(\\Gamma\\) pass through the point \\(\\left(\\frac{x}{1},(\\frac{\\alpha x}{1}+2)\\tan\\frac{\\alpha x}{8}+\\frac{x}{4} \\right)\\). (7 marks) ', '* [16] ', '7. (a) Let \\(A,B\\) be two square matrices of the same order. If \\(AB=BA\\), show by mathematical induction that for any positive integer \\(n,(A+B)^{n}=\\sum\\limits_{i=0}^{n}C_{r}^{n}A^{n-i}B^{n}\\), where \\(A^{0}\\) and \\(B^{0}\\) are by definition the identity matrix \\(I\\). (b) Let \\(A=\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\\\ \\sin\\theta&\\cos\\theta\\end{pmatrix}\\) where \\(\\theta\\in\\mathbb{R}\\). It is given that \\(A^{n}=\\begin{pmatrix}\\cos\\alpha\\theta&-\\sin\\alpha\\theta\\\\ \\sin\\alpha\\theta&\\cos\\alpha\\theta\\end{pmatrix}\\) for all positive integers \\(n\\). Using the result of (a), prove that \\[\\sum\\limits_{r=0}^{n}C_{r}^{n}\\cos\\left(n-2r\\right)\\theta=2^{n}\\cos^{n}\\theta \\ \\ \\text{and}\\ \\ \\sum\\limits_{r=0}^{n}C_{r}^{n}\\sin\\left(n-2r\\right)\\theta=0\\,.\\] (7 marks) ', '11. Consider the system of linear equations in real variables \\(x\\), \\(y\\) and \\(z\\) \\[(E):\\,\\begin{cases}\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad \\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad\\quad ', '12. Let \\(F_{b}=0\\), \\(F_{1}=1\\) and \\(F_{n+1}=F_{n}+F_{n-1}\\) for all positive integers \\(n\\) and let \\(A=\\begin{pmatrix}0&1\\\\ 1&1\\end{pmatrix}\\). 1. Prove that \\(A^{n}=\\begin{pmatrix}F_{k-1}&F_{k}\\\\ F_{n}&F_{n+1}\\end{pmatrix}\\) for all positive integers \\(n\\). (2 marks) 2. (i)  Prove that \\(F_{n+m-1}=F_{k}F_{m}+F_{n-1}\\) for all positive integers \\(m\\) and \\(n\\). 2. Prove that \\(F_{n-1}F_{n+1}-F_{n}^{2}=(-1)^{n}\\) for all positive integers \\(n\\). (c) (i)  Let \\(\\alpha\\) and \\(\\beta\\) be real roots of \\(\\mathcal{N}^{2}-\\lambda-1=0\\), where \\(\\alpha>\\beta\\). Prove that \\(A\\begin{pmatrix}1\\\\ \\alpha\\end{pmatrix}=\\mu_{1}\\begin{pmatrix}1\\\\ \\alpha\\end{pmatrix}\\) for some \\(\\mu_{1}\\in\\mathbb{R}\\) and \\(A\\begin{pmatrix}1\\\\ \\beta\\end{pmatrix}=\\mu_{2}\\begin{pmatrix}1\\\\ \\beta\\end{pmatrix}\\) for some \\(\\mu_{2}\\in\\mathbb{R}\\). (ii)  Hence, using (a), prove that \\(F_{n}=\\frac{1}{\\sqrt{6}}\\left[\\left(\\frac{1+\\sqrt{6}}{2}\\right)^{n}-\\left( \\frac{1-\\sqrt{6}}{2}\\right)^{n}\\right]\\) for all non-negative integers \\(n\\). (6 marks)  Page 29 of 32  Please go on to the next page...\n\n ', '* [19] ']
    rawLatexListBundle = Converter.kBundle(rawLatexList, 3) # >5 is very inaccurate

    # Small bundle -> Async
    parsedLatexJsonList = await extractRawLatex(rawLatexListBundle)

    # print("PARSING")
    parsedQuestions = []
    for element in parsedLatexJsonList:
        # print(type(element))
        # print(element)
        currentJson=json.loads(element)
        for question in currentJson["Questions"]:
            parsedQuestions.append(question)
    # print(list(parsedQuestions))

    Debugger.printList(parsedQuestions, "Parsed Questions")

if __name__ == "__main__":
    init_environment()
    asyncio.run(main())
    
# The model will init --> very very very slow
# ClarifaiAPI = 15calls / second, async iter
# Extract questions using DeepSeek for every 5 page as a bundle
# JSON Output for each question, including subquestions: https://api-docs.deepseek.com/guides/json_mode
# Parse JSON -> a list -> vector embedding 
# NOUGAT: MISSING PAGE POST & Sometimes it outputs random stuff like 200 \quad
# Struggles with p11 large latex text
#
# {
    # "Questions": [
    #     "Prove that \(A^{n}=\begin{pmatrix}F_{n-1}&F_{n}\\ F_{n}&F_{n+1}\end{pmatrix}\) for all positive integers \(n\).",
    #     "Prove that \(F_{n+m-1}=F_{n}F_{m}+F_{n-1}F_{m-1}\) for all positive integers \(m\) and \(n\).",
    #     "Prove that \(F_{n-1}F_{n+1}-F_{n}^{2}=(-1)^{n}\) for all positive integers \(n\).",
    #     "Let \(\alpha\) and \(\beta\) be real roots of \(x^{2}-x-1=0\), where \(\alpha>\beta\). Prove that \(A\begin{pmatrix}1\\ \alpha\end{pmatrix}=\mu_{1}\begin{pmatrix}1\\ \alpha\end{pmatrix}\) for some \(\mu_{1}\in\mathbb{R}\) and \(A\begin{pmatrix}1\\ \beta\end{pmatrix}=\mu_{2}\begin{pmatrix}1\\ \beta\end{pmatrix}\) for some \(\mu_{2}\in\mathbb{R}\).",
    #     "Hence, using (a), prove that \(F_{n}=\frac{1}{\sqrt{5}}\left[\left(\frac{1+\sqrt{5}}{2}\right)^{n}-\left( \frac{1-\sqrt{5}}{2}\right)^{n}\right]\) for all non-negative integers \(n\)."
    # ]
# }
