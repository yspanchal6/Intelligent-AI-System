# Testing and Evaluation

## Unit tests

Run the tests that are present in your checkout. For the full clean source package, a typical command is:

```bash
python -m unittest test_task_engine.py test_task_manager.py test_decision_engine.py test_automation_engine.py test_chatbot_engine.py -v
```

If a named test file is absent from your project version, remove it from the command. Inspect the test source before running tests that write to local data.

## Gemini integration test

If `test_gemini.py` is included and requires a live API, run it only after configuring a valid API key:

```bash
python -m unittest test_gemini.py -v
```

A skipped test, missing API key, quota error, or provider outage is not a successful integration result. Record these outcomes accurately.

## Classifier evaluation

```bash
python evaluation.py
python compare_models.py
```

Copy the actual output into the college report. Record the dataset/split size and the reported accuracy, precision, recall, F1-score, and confusion matrix when available. Do not invent metric values or imply that a small test split proves performance on all real-world inputs.

## Manual test checklist

| ID | Test | Expected behavior | Actual result |
|---|---|---|---|
| T-01 | Enter help command | Show supported commands | Record after execution |
| T-02 | Submit a basic arithmetic request | Return the correct result or a safe validation message | Record after execution |
| T-03 | Add and list a task | Persist and display task data | Record after execution |
| T-04 | Complete a task by ID | Mark the selected task complete or explain invalid ID | Record after execution |
| T-05 | Submit an offline knowledge question | Answer only if the topic is supported locally | Record after execution |
| T-06 | Search the web | Return results or report service failure clearly | Record after execution |
| T-07 | Ask a general question with Gemini configured | Return a response when provider access works | Record after execution |
| T-08 | Trigger a confirmed external action | Ask for confirmation and perform only the described action | Record after execution |

## Evidence for reports

Use real screenshots from the application terminal. Crop them to the relevant output, avoid showing secrets or personal task data, and label each screenshot with a figure number and caption.
