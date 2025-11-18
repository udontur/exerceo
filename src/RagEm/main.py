import Settings as Settings

def embedQuestions(questionList):
    curIdList = []
    for i in range(len(questionList)):
        curIdList.append(f"{Settings.ragDb.count()}")
    Settings.ragDb.add(
        ids=curIdList,
        documents=questionList,
    )

def queryQuestion(question):
    results = Settings.ragDb.query(
        query_texts=[question],
        n_results=Settings.ragNResults,
    )
    return results