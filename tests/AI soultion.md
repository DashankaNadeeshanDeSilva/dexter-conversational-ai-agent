===== Result =====
{'messages': [HumanMessage(content='Who is current the president of Sri Lanka ?', additional_kwargs={}, response_metadata={}), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_yoi5xjvWmlciCpeB5rJomVn2', 'function': {'arguments': '{"query":"current president of Sri Lanka 2023"}', 'name': 'internet_search'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 21, 'prompt_tokens': 534, 'total_tokens': 555, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_34a54ae93c', 'id': 'chatcmpl-C0V7thwRMbvPxatt8MQa93QzsNRfO', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--391cc6f9-bf2f-4fc2-8bc4-3d83a908a25c-0', tool_calls=[{'name': 'internet_search', 'args': {'query': 'current president of Sri Lanka 2023'}, 'id': 'call_yoi5xjvWmlciCpeB5rJomVn2', 'type': 'tool_call'}], usage_metadata={'input_tokens': 534, 'output_tokens': 21, 'total_tokens': 555, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}), ToolMessage(content='1. President of Sri Lanka - Wikipedia\nThe president of Sri Lanka ( Sinhala : ශ් රී ලංකා ජනාධිපති Śrī La ... The governor-general was replaced by the office of President of Sri Lanka . ... The protestors also demanded amendments to the Constitution of Sri Lanka and to reduce the powers of the President .\nSource: https://en.wikipedia.org/wiki/President_of_Sri_Lanka\n\n2. Prime Minister of Sri Lanka - Wikipedia\nIn recent years, Temple Trees has also been used by some presidents of Sri Lanka , such as Kumaratunga and Rajapaksa , while some prime ministers such as Wickremesinghe have chosen to stay at their own personal residences. ... Sri Lankan order of precedence , the prime minister is placed after the ...\nSource: https://en.wikipedia.org/wiki/Prime_Minister_of_Sri_Lanka\n\n3. Sri Lanka election 2024: Who could be the next president, what’s at stake? – DNyuz\n... of Sri Lanka ’s Constitution, passed in ... The incumbent president has governed with the backing of the Sri Lanka Podujana Peramuna (SLPP) party of the Rajapaksa family. ... Premadasa, son of former President Ranasinghe Premadasa, is the current leader of opposition in Sri Lanka ’s parliament.\nSource: https://dnyuz.com/2024/09/20/sri-lanka-election-2024-who-could-be-the-next-president-whats-at-stake/\n\n4. Sri Lanka President expresses dissatisfaction with country\'s current education system - Sri\nSri Lanka President Ranil Wickremesinghe has called for a fresh analysis of the life and character of King Sitawaka Rajasingha, a courageous and patriotic king of historical significance. ... faced by the Sri Lankan people, Ambassador Qi expressed confidence that, under the leadership of President ...\nSource: https://www.onlanka.com/news/sri-lanka-president-expresses-dissatisfaction-with-countrys-current-education-system.html\n\n5. Anura Kumara Dissanayake: Who is Sri Lanka’s new president? (2025)\nFormer president Gotabaya Rajapaksa was driven out of Sri Lanka in 2022 by mass protests sparked by the ... Though I heavily campaigned for President Ranil Wickremesinghe, the people of Sri Lanka have made their decision, and I fully respect their mandate for Anura Kumara Dissanayake," Sabry said.\nSource: https://truvapark.com/article/anura-kumara-dissanayake-who-is-sri-lanka-s-new-president\n', name='internet_search', tool_call_id='call_yoi5xjvWmlciCpeB5rJomVn2'), AIMessage(content='The current president of Sri Lanka is Ranil Wickremesinghe.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 16, 'prompt_tokens': 980, 'total_tokens': 996, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_34a54ae93c', 'id': 'chatcmpl-C0V7vvcGnnLnllXXeW86vULATZPqW', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='run--0c345597-c5b7-418f-9cc1-8324bad590b1-0', usage_metadata={'input_tokens': 980, 'output_tokens': 16, 'total_tokens': 996, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})], 'user_id': 'dashanka_1', 'conversation_id': '688a8a939687546434794c57', 'session_id': 'e62df255-0b78-448e-a88d-ca01feb4014a', 'tools': [WebSearchTool()], 'tool_names': ['internet_search']}





(dexter) dashankadesilva@Dashankas-MacBook-Air-4 dexter-conversational-ai-agent % python upsert_knowledge.py
/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py:3: LangChainDeprecationWarning: Importing PyPDFLoader from langchain.document_loaders is deprecated. Please replace deprecated imports:

>> from langchain.document_loaders import PyPDFLoader

with new imports of:

>> from langchain_community.document_loaders import PyPDFLoader
You can use the langchain cli to **automatically** upgrade many imports. Please see documentation here <https://python.langchain.com/docs/versions/v0_2/>
  from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, DirectoryLoader
/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py:3: LangChainDeprecationWarning: Importing Docx2txtLoader from langchain.document_loaders is deprecated. Please replace deprecated imports:

>> from langchain.document_loaders import Docx2txtLoader

with new imports of:

>> from langchain_community.document_loaders import Docx2txtLoader
You can use the langchain cli to **automatically** upgrade many imports. Please see documentation here <https://python.langchain.com/docs/versions/v0_2/>
  from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, DirectoryLoader
/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py:3: LangChainDeprecationWarning: Importing TextLoader from langchain.document_loaders is deprecated. Please replace deprecated imports:

>> from langchain.document_loaders import TextLoader

with new imports of:

>> from langchain_community.document_loaders import TextLoader
You can use the langchain cli to **automatically** upgrade many imports. Please see documentation here <https://python.langchain.com/docs/versions/v0_2/>
  from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, DirectoryLoader
/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py:3: LangChainDeprecationWarning: Importing DirectoryLoader from langchain.document_loaders is deprecated. Please replace deprecated imports:

>> from langchain.document_loaders import DirectoryLoader

with new imports of:

>> from langchain_community.document_loaders import DirectoryLoader
You can use the langchain cli to **automatically** upgrade many imports. Please see documentation here <https://python.langchain.com/docs/versions/v0_2/>
  from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, DirectoryLoader
Traceback (most recent call last):
  File "/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py", line 78, in <module>
    main("app/db_clients/upsert_data/company_data.txt")
  File "/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py", line 71, in main
    upsert_documents(documents)
  File "/Users/dashankadesilva/Drive/Projects/project Dexter/Dexter v1.0/dexter-conversational-ai-agent/upsert_knowledge.py", line 63, in upsert_documents
    pinecone_client.vector_store.add_documents(document_chunks)
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/langchain_core/vectorstores/base.py", line 288, in add_documents
    return self.add_texts(texts, metadatas, **kwargs)
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/langchain_pinecone/vectorstores.py", line 356, in add_texts
    [res.get() for res in async_res]
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/langchain_pinecone/vectorstores.py", line 356, in <listcomp>
    [res.get() for res in async_res]
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/multiprocessing/pool.py", line 774, in get
    raise self._value
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/multiprocessing/pool.py", line 125, in worker
    result = (True, func(*args, **kwds))
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/pinecone/openapi_support/api_client.py", line 182, in __call_api
    raise e
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/pinecone/openapi_support/api_client.py", line 170, in __call_api
    response_data = self.request(
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/pinecone/openapi_support/api_client.py", line 386, in request
    return self.rest_client.POST(
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/pinecone/openapi_support/rest_utils.py", line 146, in POST
    return self.request(
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/pinecone/openapi_support/rest_urllib3.py", line 267, in request
    return raise_exceptions_or_return(r)
  File "/Users/dashankadesilva/Applications/miniconda3/envs/dexter/lib/python3.10/site-packages/pinecone/openapi_support/rest_utils.py", line 49, in raise_exceptions_or_return
    raise PineconeApiException(http_resp=r)
pinecone.exceptions.exceptions.PineconeApiException: (400)
Reason: Bad Request
HTTP response headers: HTTPHeaderDict({'date': 'Mon, 04 Aug 2025 16:11:20 GMT', 'content-type': 'application/json', 'content-length': '103', 'x-pinecone-request-latency-ms': '438', 'x-pinecone-request-id': '8863122195509282104', 'x-envoy-upstream-service-time': '22', 'server': 'envoy'})
HTTP response body: {"code":3,"message":"Vector dimension 1536 does not match the dimension of the index 512","details":[]}

(dexter) dashankadesilva@Dashankas-MacBook-Air-4 dexter-conversational-ai-agent % 
