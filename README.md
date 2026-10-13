# Data Analyst Agent

A Python agent that answers questions about a sales dataset. A local language model decides which tool to run. Pandas does the calculations, matplotlib draws charts, and scikit-learn trains a regression model. The agent runs on your own computer through Ollama, so it costs nothing to run.

## What it does

- Answers questions about revenue, order counts, and discounts by running pandas code
- Saves bar and line charts as PNG files in `outputs/`
- Trains a linear regression model to predict revenue and reports its test R2 score

## How it works

The agent runs a loop:

1. The model receives your question and the list of available tools.
2. If the model requests a tool, the agent runs it and sends the result back.
3. The loop repeats until the model replies with plain text, or until it reaches 8 steps.

Errors come back to the model as text. When pandas code fails, the model reads the error and tries again.

| Tool | What it does |
|---|---|
| `describe_dataset` | Returns the row count, column types, valid values for `region` and `product`, and the first five rows |
| `run_pandas` | Runs pandas code the model writes. The code stores its answer in a variable called `result` |
| `make_chart` | Groups a numeric column and saves a bar or line chart as a PNG |
| `train_revenue_model` | Trains a linear regression on quantity, discount, and product, and returns the test R2 score |

## Project structure

```
data-analyst-agent/
├── data/                  # sales.csv (500 rows)
├── docs/                  # screenshots for this README
├── outputs/               # charts saved by the agent
├── agent.py               # agent loop and tool definitions
├── tools.py               # functions the agent can call
├── make_sample_data.py    # creates the sample sales data
├── check.py               # computes the correct answers for testing
├── compare_models.py      # compares linear regression with random forest
├── eval_log.md            # test results
├── requirements.txt
└── README.md
```

## Tech stack

| Component | Purpose | Cost |
|---|---|---|
| Python 3.12 | Runtime | Free |
| pandas | Data loading and analysis | Free |
| matplotlib | Charts | Free |
| scikit-learn | Machine learning | Free |
| Ollama | Runs the model on your computer | Free |
| Qwen2.5 7B | Language model that chooses the tools | Free |

Total cost: AED 0.

## Setup

**Requirements:** Windows or macOS, 16 GB of RAM recommended, about 8 GB of free disk space.

1. Install Ollama from ollama.com, open it, and download the model. Ollama must be running when you use the agent.

```powershell
   ollama pull qwen2.5:7b
```

2. Clone the repository and open the folder.

```powershell
   git clone https://github.com/YOUR-USERNAME/data-analyst-agent.git
   cd data-analyst-agent
```

3. Create and activate a virtual environment. On macOS or Linux, use `python3` and `source .venv/bin/activate` instead.

```powershell
   python -m venv .venv
   .venv\Scripts\activate
```

4. Install the packages.

```powershell
   pip install -r requirements.txt
```

5. Run the agent and type a question at the prompt.

```powershell
   python agent.py
```

   Try this question first: `Which region has the highest total revenue_aed?`

To regenerate the sample data, run `python make_sample_data.py`. This overwrites `data/sales.csv` with the same 500 rows, because the script uses a fixed random seed.

## Evaluation

I asked five questions and checked each agent answer against a pandas calculation in `check.py`.

| # | Question | First run | After fix |
|---|---|---|---|
| 1 | Which region has the highest total revenue_aed? | Right | Right |
| 2 | How many orders were placed in March 2025? | Right | Right |
| 3 | What is the average discount on Laptop orders? | Right | Right |
| 4 | What is the total revenue for Phones? | Wrong (returned 0 AED) | Right |
| 5 | Draw a bar chart of revenue_aed by product. | Right | Right |

| Metric | Result |
|---|---|
| Correct answers, first run | 4 of 5 |
| Correct answers, after fix | [5 of 5] |
| Average tool calls per question | [2] |
| Average time per question | [58.7] seconds |
| Test R2, linear regression | [0.841] |
| Test R2, random forest | [1.000] |

## Before and after: the Phone revenue bug

On the first run, the agent reported that Phone revenue was 0 AED. The data uses `Phone`, but the agent filtered on `phones`. Pandas comparisons are exact and case-sensitive, so the filter matched no rows, and the sum of zero rows is 0. The model reported that 0 without checking it.

I made two changes:

1. `describe_dataset` now lists the valid values for `region` and `product`, so the model can see the exact category names before it writes a filter.
2. The system prompt tells the model to check the valid values and try again whenever a filter returns 0.

After the change, the agent returned [the correct total of X AED on the first try / the correct total after N tool calls].

## Known limitations

- The 7B model sometimes picks a wrong column or category name on the first try. Listing the valid values reduces this, but it does not remove it.
- `run_pandas` uses `exec` to run code the model writes. Use this project only with your own data on your own computer.
- The regression model is simple. A linear model cannot fully capture how quantity and discount multiply together, so its R2 score is moderate.
- The test set has only five questions. A larger test set would give a more reliable accuracy figure.
- The model runs without a dedicated GPU, so each question takes [50 to 70] seconds on my laptop.

## Next steps

- Log every agent step to a JSONL file for later analysis
- Add a random forest as a second ML tool the agent can choose from
- Build a Streamlit interface so users can ask questions in a browser
