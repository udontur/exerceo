## Backend
- Like obsidian, a folder that hosts everything
- OCR model on premise

## Fontend
- A GTK app
- Can add or remove PDFs like NotebookLM
- Middle display the generated LaTeX paper
- Right bar select which paper to use
- Show how many credits you have used 
- Distribute through flatpak with Docker and Nix
- Connects to the backend directly (bundled togeather)


# TODO: Refactor vector embedding code
# TODO: Make OCR run on Premise
# TODO: Make a user input query the vector database
# TODO: Make the vector DB persistent
# TODO: RAG search (deepseek) using vector dartabase
# TODO: clean up the repo structure and assets
# Turn systenv into settings

# TODO: Generate new papers with similar questions + user prompt (with full LaTeX)
# TODO: Make a docker so that every utility needed is inside of docker (so you only need docker to start developing)

