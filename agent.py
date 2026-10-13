import ollama

from tools import describe_dataset, make_chart, run_pandas
from tools import describe_dataset, make_chart, run_pandas, train_revenue_model

MODEL = "qwen2.5:7b"  # change this if you pulled a different model
MAX_STEPS = 8         # stops runaway loops

SYSTEM_PROMPT = (
    "You are a data analyst. Always call describe_dataset first, before any other tool. "
    "When you filter on region or product, use the exact values listed in text_column_values, "
    "including capital letters and singular forms. "
    "Calculate every number with run_pandas. Never guess a number. "
    "If a filter returns 0 or an empty result, call describe_dataset to check the values and try again "
    "before you answer. "
    "The columns are date, region, product, quantity, discount, revenue_aed, month. "
    "Keep the final answer short and state the numbers clearly."
)

# Tool descriptions the model reads to decide what to call
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "describe_dataset",
            "description": "Show the row count, column names with types, and the first 5 rows. Call this first.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_pandas",
                "description": (
                "Run pandas code on the dataframe df. Columns: date, region, product, "
                "quantity, discount, revenue_aed, month. Text values are case-sensitive, "
                "so use the exact values from describe_dataset. "
                "Store the final answer in a variable called result."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code that uses df and pd"},
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_chart",
            "description": "Save a bar or line chart that sums a numeric column for each group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {"type": "string", "description": "Column to group by, such as region, product, or month"},
                    "value": {"type": "string", "description": "Numeric column to sum, such as revenue_aed"},
                    "chart_type": {"type": "string", "enum": ["bar", "line"]},
                    "title": {"type": "string"},
                    "filename": {"type": "string", "description": "File name ending in .png"},
                },
                "required": ["group_by", "value", "chart_type", "title", "filename"],
            },
        },
    },
        {
        "type": "function",
        "function": {
            "name": "train_revenue_model",
            "description": "Train a model that predicts revenue_aed from quantity, discount, and product. Returns the test R2 score.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# Map each tool name to the real Python function
TOOL_FUNCTIONS = {
    "describe_dataset": describe_dataset,
    "run_pandas": run_pandas,
    "make_chart": make_chart,
    "train_revenue_model": train_revenue_model,
}


def call_tool(name, arguments):
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Error: there is no tool called {name}."
    try:
        return str(func(**arguments))
    except Exception as e:
        return f"Error calling {name}: {e}"


def run_agent(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        message = response.message
        messages.append(message)

        # No tool requested means the model has its final answer
        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            arguments = call.function.arguments
            print(f"[step {step}] calling {name} with {arguments}")
            result = call_tool(name, arguments)
            messages.append({"role": "tool", "content": result})

    return "Stopped: the agent reached the step limit before finishing."


if __name__ == "__main__":
    question = input("Ask a question about the sales data: ")
    print("\nAnswer:\n" + run_agent(question))