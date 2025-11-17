# Local
import Sysenv
import PdfParser.Llms as LLMs

# Utilities
import pymupdf
import asyncio
# import time


def pdfToImages(pdfFilePath):
    pdfBinary = open(pdfFilePath, "rb").read()
    pdfDocument = pymupdf.open(
        stream=pdfBinary,
        filetype="pdf",
    )

    imageList = []
    for pdfPage in pdfDocument:
        currentPixmap = pdfPage.get_pixmap(matrix=Sysenv.pixmapScale)
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

# Check if the ratelimit coros work
async def concurrentProcess(coros, item):
    result = []
    for startIndex in range(0, len(coros), Sysenv.maxConcurrentApiRequests):
        endIndex=min(startIndex+ Sysenv.maxConcurrentApiRequests, len(coros))
        batch = coros[startIndex : endIndex]

        print(f"[OCR] Started processing {startIndex}-{endIndex}/{len(coros)} {item}.")
        batchResult=await asyncio.gather(*batch)
        print(f"[OCR] Finished processing {startIndex}-{endIndex}/{len(coros)} {item}.")

        result.extend(batchResult)
        await asyncio.sleep(1)

    return result


async def extractRawLatex(rawLatexList):
    coros = []
    for latexBundle in rawLatexList:
        coro = LLMs.rawLatexToParsedLatex(rawLatex=latexBundle)
        coros.append(coro)

    result = await concurrentProcess(coros, "latex texts")
    return result


async def imagesToLatex(imageList):
    coros = []
    for image in imageList:
        coro = await LLMs.imageToLatex(imageBytes=image)
        coros.append(coro)

    result = await concurrentProcess(coros, "images")
    return result
