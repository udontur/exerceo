import Sysenv

def embedQuestions(questionList):
    curIdList = []
    for i in range(len(questionList)):
        curIdList.append(f"{Sysenv.ragNumberOfRecords+1}")
        Sysenv.ragNumberOfRecords+=1
    Sysenv.ragDb.add(
        ids=curIdList,
        documents=questionList,
    )

def queryQuestion(question):
    results = Sysenv.ragDb.query(
        query_texts=[question],
        n_results=3,
    )
    return results