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


# TODO: add a rate limit for the coros
async def extractRawLatex(rawLatexList):
    coros = []
    # TODO: Print how many out of how many it is doing now
    for latexBundle in rawLatexList:
        coro = LLMs.rawLatexToParsedLatex(rawLatex=latexBundle)
        coros.append(coro)
    return await asyncio.gather(*coros)


# Turns a image list into Latex, maps individual image to a list
async def imagesToLatex(imageList):
    coros = []
    # TODO: Print how many out of how many it is doing now
    for image in imageList:
        coro = await LLMs.imageToLatex(imageBytes=image)
        coros.append(coro)

    # TODO: Temporary as it can only process 1 API request per second
    # return await asyncio.gather(*coros)
    return coros
