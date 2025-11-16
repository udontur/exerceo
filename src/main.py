# Local
import Sysenv
import PdfParser.main as PdfParser
import RagEm.main as RagEm

# Utilities
import asyncio


async def main():
    parsedQuestions = await PdfParser.pdfParser("./assets/test/latex-test-1.pdf")
    Sysenv.Debugger.printList(parsedQuestions, "Parsed Questions")
    RagEm.embedQuestions(parsedQuestions)
    print(RagEm.queryQuestion("Trigonometry and matrix"))

if __name__ == "__main__":
    Sysenv.init_environment()
    asyncio.run(main())


