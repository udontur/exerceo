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

# GTK app, distribute through flatpak only
# Everything is located in the local folder
# The app opens a folder that hosts the vector database (local)
# TODO: a list -> vector embedding
# TODO: RAG search using vector database
# TODO: Generate new test paper with similar questions
# TODO: Make solutions for the test paper and practice questions
# TODO: Can input prompts and predefined prompts
# I want to learn about APIs, servers, dockers, and hosting stuff
# TODO: Docker and kubernets
