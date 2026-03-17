GRADER_PROMPT = """You are a teacher grading a quiz. 
You will be given a QUESTION, a CONTEXT, and a STUDENT ANSWER.

Here is the grade criteria to follow:
1. The STUDENT ANSWER must be fully supported by the CONTEXT.
2. The STUDENT ANSWER must directly address the QUESTION.
3. If the STUDENT ANSWER mentions information not present in the CONTEXT, it is a failure (hallucination).

Score:
A "YES" means the answer is good.
A "NO" means the answer is bad (hallucination, irrelevant, or unsupported).

Explain your reasoning briefly, then provide the final score in the format: "SCORE: YES" or "SCORE: NO".

QUESTION: {question}
CONTEXT: {context}
STUDENT ANSWER: {answer}

Your Grade:"""

ROUTER_PROMPT = """You are a smart assistant routing a user query.
Your task is to decide if the query requires an EXTERNAL WEB SEARCH.

The user might ask to "compare" internal data with external/online data.
They might use words like "web", "online", "internet", "google", "search", "external", "compare with market", etc.
If the user explicitly asks for external information or comparison, output "YES".
If the query can be answered solely by local context or is general conversation, output "NO".

Query: {question}

Decision (YES or NO):"""

COMPARISON_PROMPT = """You are an expert analyst.
You have access to two sources of information:

=== 1. LOCAL INTERNAL DOCUMENTS ===
{local_context}

=== 2. EXTERNAL WEB SEARCH RESULTS ===
{web_context}

=== INSTRUCTIONS ===
Answer the user's QUESTION: "{question}".
Use both sources to provide a comprehensive answer.
If the user asked for a comparison, explicitly structure your answer to compare the specific points from the Internal Documents vs the External Web.
Highlight agreements, disagreements, or missing information in either source.
Cite the sources where possible (e.g., [Local], [Web]).

Answer:"""

METRICS_PROMPT = """You are an impartial judge evaluating the quality of an AI assistant's response.
You will be given a QUESTION, a CONTEXT, and the AI's ANSWER.

Please evaluate the answer on the following criteria from 1 to 5 (Integers):

1. **Relevance**: Does the answer directly address the specific question asked? (1 = Irrelevant, 5 = Highly Relevant)
2. **Faithfulness**: Is the answer fully supported by the provided CONTEXT? (1 = Hallucinated, 5 = Fully Supported by Context)
3. **Clarity**: Is the answer easy to understand and well-structured? (1 = Confusing, 5 = Very Clear)

Output ONLY a JSON-like format as follows, with no other text:
{{
"relevance": <score>,
"faithfulness": <score>,
"clarity": <score>,
"reasoning": "<short explanation>"
}}

QUESTION: {question}
CONTEXT: {context}
ANSWER: {answer}
"""
