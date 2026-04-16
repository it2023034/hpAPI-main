def build_triple_extraction_prompt(schema, example_dialogue, example_out, case_dialogue):
    return f"""
Task:
Extract knowledge graph triples from the input dialogue.

The input dialogue is provided as structured messages.
Each row has the form:
[Time] Sender -> Receiver: Message

Use the sender and receiver names exactly as they appear in the input.

You must output ONLY triples.
Do not output explanations.
Do not output introductory text.
Do not output bullets.
Do not output labels other than the final "Output:" line.
Do not output any relation that is not listed in the schema.
If a fact does not fit the schema, omit it.

Rules:
- Use ONLY entity names that appear explicitly in the input
- Do NOT introduce entities from the example
- Do NOT infer hidden participants
- Do NOT infer transactions, accounts, balances, or transfers unless explicitly stated
- Use sender and receiver information to infer communication relationships when appropriate
- Do not output duplicate triples

Output format:
subject | relation | object

Formatting constraints:
- Exactly one triple per line
- Use exactly one space before and after |
- No empty lines

Allowed schema:

{schema}

Example Input:
{example_dialogue}

Example Output:
{example_out}

Now process this input.

Input:
{case_dialogue}

Output:
""".strip()


def build_explanation_prompt(dialogue_text, triple):
    entity, attribute, value = triple

    return f"""
ROLE:
You are an explanation generator for knowledge triples derived from a dialogue.
The triple already exists.
Your task is NOT to explain how the triple was extracted,
but to explain why this fact appears in the dialogue.

CONTEXT:
The data below contains a dialogue.
Each triple represents a fact that is explicitly stated or clearly implied in the dialogue.
You must explain the factual reason why this information is present.

DIALOGUE:
{dialogue_text}

TRIPLE:
{entity} | {attribute} | {value}

EXAMPLES (good):
Triple:
Alice | sends | payment
Explanation:
Alice sends the payment because the dialogue includes a transfer of money initiated by her.

EXAMPLES (bad):
- Mentions extraction (e.g., "the system extracted...")
- Explains other attributes not in the triple
- Uses filler phrases (e.g., "To be clear", "Additionally", "Furthermore")
- Gives generic explanations with no connection to the dialogue

TASK:
Write ONLY ONE concise sentence explaining why this triple appears in the dialogue,
based strictly on the provided context.

RULES:
- Explain WHY this fact appears in the dialogue
- Focus strictly on the given triple
- The explanation MUST explicitly mention the given attribute and the given value
- Base the explanation on the dialogue context only when necessary
- Do NOT repeat or summarize the entire dialogue
- Do NOT introduce additional events or actions not directly tied to the triple
- Ensure the explanation matches the exact attribute and value in the triple
- Do NOT introduce unrelated attributes or values
- Do NOT add new facts or assumptions
- Do NOT include unrelated information
- Do NOT explain the extraction process
- Do NOT mention models, systems, or analysis steps
- Do NOT use phrases like "To be clear", "Additionally", "Furthermore"
- Maximum ONE sentence
- Stop immediately after the first sentence
- Natural language only
- Keep the explanation concise and specific

OUTPUT:
""".strip()
