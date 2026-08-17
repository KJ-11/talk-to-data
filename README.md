# talk-to-data

Upload a spreadsheet, ask questions about it in plain English, get answers back.

Some questions need a database query. Some just need an answer. This app decides which, per question, then runs the query if there is one.

## How the routing works

This is the interesting part, so it goes first.

There is no separate classifier and no "is this SQL?" pre-check on the user's question. The app sends one prompt to GPT-4 containing the user's question, the table name (`uploaded_data`), and the exact column names pulled from the uploaded file. The prompt tells the model it can either answer directly or return a SQL query, whichever fits.

The routing decision is then made by reading the model's reply, not the user's question. In `generate_response_or_query` (`streamlit_app/main.py`), the reply is treated as SQL if either is true:

- it starts with `select` (case insensitive), or
- the substring `from` appears anywhere in it

If the reply is classified as SQL, `extract_sql_query` pulls the statement out with the regex `(SELECT .*?;)`, so surrounding prose from the model gets discarded. The statement runs against SQLite via `execute_sql_query` and the rows are printed. Otherwise the reply is printed as prose.

So the model picks the strategy and the app infers that choice from the shape of the response.

## Example

Upload a customer CSV with columns like `CustomerId`, `Geography`, `CreditScore`, `Balance`, `Exited`.

Ask:

> What is the average credit score of customers in Germany who churned?

The model returns a `SELECT`, the app spots it, extracts it, and runs it:

```sql
SELECT AVG("CreditScore") FROM uploaded_data WHERE "Geography" = 'Germany' AND "Exited" = 1;
```

You get the number back.

Ask instead:

> What kinds of questions can I ask about this dataset?

No `SELECT`, no `from`, so the app prints the model's prose answer and never touches the database.

## What it does

1. You upload a CSV, XLSX, TXT, or TSV file in the sidebar.
2. pandas reads it into a DataFrame.
3. The DataFrame is written to a local SQLite database as a table called `uploaded_data`, replacing whatever was there before.
4. The first 10 rows and the column list are shown as a preview.
5. You ask questions in the chat panel and the routing above takes over.

Column names are passed to the model quoted, so columns with spaces or mixed case survive the round trip.

## Stack

- Python
- Streamlit (UI, file upload, layout)
- pandas (file parsing)
- SQLite via the stdlib `sqlite3` (query engine)
- OpenAI GPT-4 (routing and SQL generation)
- python-dotenv (API key loading)

## Running it locally

You need Python 3.9+ and an OpenAI API key.

```bash
git clone https://github.com/KJ-11/talk-to-data.git
cd talk-to-data

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the repo root:

```
OPENAI_API_KEY=sk-your-key-here
```

Then run:

```bash
streamlit run streamlit_app/main.py
```

It opens at `http://localhost:8501`. Upload a file in the sidebar, then ask a question on the right.

The SQLite file is created at `streamlit_app/db/temp.db` on first upload. It is scratch space, it gets overwritten on every upload, and it is gitignored.

## Known limitations

Worth being straight about these:

- The `from` substring check is loose. A prose answer containing the word "from" in an ordinary sentence gets routed down the SQL path, where the regex finds no `SELECT` and the query comes back empty.
- Queries are executed as returned by the model. Fine for local use on your own file, not safe to expose to untrusted input.
- Only one table exists at a time. Uploading a new file replaces the previous one.
- `streamlit_app/chat.py` is an earlier LangChain based attempt that `main.py` does not import. It is left in the history but is not part of the running app.
