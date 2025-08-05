from app.tools.semantic_retrieval_tool import KnowledgeRetrievalTool

semantic_retrieval_tool = KnowledgeRetrievalTool()
query = "Whar Services Offered ?"
result = semantic_retrieval_tool._run(query)
print("Retrieved context: ", result)