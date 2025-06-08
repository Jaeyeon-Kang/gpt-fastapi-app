# GPT Prompt Behavior Tester (FastAPI)

A lightweight FastAPI server integrated with OpenAI's Chat Completion API.
Designed for testing and comparing different prompt configurations — including system roles and temperature values — in a structured and reproducible way.

---

## Features

* Prompt customization via `system` role and `temperature`
* Automatic logging of responses to CSV for later analysis
* Modular structure for rapid experimentation and extension
* Compatible with Codespaces, easily deployable in cloud environments

---

## Project Structure

```
gpt-fastapi-app/
├── main.py                    # FastAPI server
├── config.py                  # OpenAI API key loading
├── prompt_template.py         # Prompt constructor and parameter definitions
├── experiments/
│   └── run_prompt_test.py     # Batch experiment runner (role × temp × prompt)
├── logs/
│   └── chat_logs.csv          # Prompt-response log
├── .env                       # (not committed) Your OpenAI API key
├── requirements.txt
```

---

## How to Use

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your OpenAI API key to `.env`

```
OPENAI_API_KEY=sk-...
```

### 3. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Test via Swagger UI

Visit `http://localhost:8000/docs`, enter a prompt in the `POST /chat` endpoint.

---

## Batch Testing

To generate multiple responses for evaluation:

```bash
python -m experiments.run_prompt_test
```

Each combination of prompt × system role × temperature will be logged to `logs/chat_logs.csv`.

---

## Prompt Experimentation

The system is designed to help explore:

* How different **system roles** shape the tone and framing of responses
* How **temperature** affects creativity, specificity, and variability
* How **the same user input** can yield different responses depending on context

This enables prompt engineers or AI practitioners to better understand GPT behavior under structured experimental conditions.

---

## License

MIT
