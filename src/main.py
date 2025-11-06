# Local
import Sysenv
import PdfParser.main as PdfParser

# Utilities
import asyncio


async def main():
    parsedQuestions = await PdfParser.pdfParser("./assets/test/latex-test-1.pdf")
    Sysenv.Debugger.printList(parsedQuestions, "Parsed Questions")


if __name__ == "__main__":
    Sysenv.init_environment()
    asyncio.run(main())

# TODO: a list -> vector embedding
# TODO: Make this a API backend and connect to MGL's front end
# TODO: Docker and kubernets
