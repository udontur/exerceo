# Local
import Settings as Settings
import PdfParser.main as PdfParser
import RagEm.main as RagEm

# Utilities
import asyncio


async def main():
    parsedQuestions = await PdfParser.pdfParser("./test/latex-test-1page.pdf")
    Settings.Debugger.printList(parsedQuestions, "Parsed Questions")
    RagEm.embedQuestions(parsedQuestions)

    queryQuestion=input("Enter a question to query: ")
    while queryQuestion!="q":
        print(RagEm.queryQuestion(queryQuestion))
        queryQuestion=input("Enter a question to query: ")

if __name__ == "__main__":
    Settings.init_environment()
    asyncio.run(main())


