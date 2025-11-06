# Local
import PdfParser.Converter as Converter


async def pdfParser(filePath):
    pdfImageList = Converter.pdfToImages(filePath)

    rawLatexList = await Converter.imagesToLatex(pdfImageList)
    rawLatexListBundle = Converter.kBundle(rawLatexList, 3)  # >5 is very inaccurate

    parsedLatexList = await Converter.extractRawLatex(rawLatexListBundle)
    parsedQuestions = Converter.flattenList(parsedLatexList)

    return parsedQuestions
