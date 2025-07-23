

AI agent graph raw responsefor given user query:
```bash
AgentState(
    messages=[
        HumanMessage(content="What's the weather like in San Francisco today?"),
        
        AIMessage(content="I'll check the weather in San Francisco for you.", tool_calls=[
            ToolCall(name="search", args='{"query": "current weather San Francisco"}')
        ]),
        
        FunctionMessage(name="search", content='Results: San Francisco, CA weather: Currently 68°F and partly cloudy. High today 72°F with light westerly winds.'),
        
        AIMessage(content="The weather in San Francisco today is 68°F and partly cloudy. The forecast shows a high of 72°F with light westerly winds.")
    ],
    user_id="user123",
    session_id="session456",
    conversation_id="convo789",
    tools=[SearchTool()],
    tool_names=["search"]
)
```

### Message Flow in This Example
* User Input: A HumanMessage with the user's query
* Tool Decision: An AIMessage where the agent decides to use a tool (note the tool_calls attribute)
* Tool Output: A FunctionMessage containing the results from executing the search tool
* Final Response: Another AIMessage with the agent's final response that incorporates the tool results


temp prompt:

I think you did a good job by introducing new set of functions and code snippets with midifcations to memory_manager and agent scripts which are semantic fact extraction and storing system, and method to consolidate session and conversation level knowledge. 
Now I ant you to answer following:
* Explain the logic in the consoldation method.
* Can you check if there are ways to extract the semntic and contextual fact extraction without involving LLM invokation as this step is costly and increase the latency.
Dont do any coding but discuss first !

-------
* memory_manager script has gotton too large and complex, needs to simplify and modularize.

next step: 
* Apply the  consoldation method at the end of the chat session not in the middle of the chat (not after every user-agent chat pair interaction but at the end of the chat)
* 

## Tools:

### ProductSearchTool:
✅ Product discovery - Find products by name, category, features
✅ Price filtering - "under $100", "between $50-200"
✅ Inventory checking - "in stock", "available"
✅ Category browsing - "electronics", "clothing"
✅ Specification search - "wireless headphones", "iPhone cases"

### ProductSearchTool Capabilities:
"Find wireless headphones under $100" → Price + category filtering
"Show electronics in stock" → Category + availability filtering
"Laptops between $500 and $1000" → Price range filtering

### AppointmentTool:
✅ Availability checking - "available appointments tomorrow"
✅ Appointment booking - "schedule consultation with Dr. Smith"
✅ Appointment modification - "reschedule my appointment"
✅ Schedule viewing - "show Dr. Smith's schedule"
✅ Cancellation - "cancel my appointment"

### AppointmentTool Capabilities:
"Book appointment tomorrow at 2pm" → Create appointment
"Cancel appointment ABC12345" → Cancel with ID
"Reschedule my appointment to Friday at 10am" → Update appointment
"Show my appointments" → View user appointments
"Available appointments next week" → Search availability