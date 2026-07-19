# Architecture

`domain` contains deterministic models and calculations. `adapters` validates CSV
input. `services` orchestrates scenario evaluation and report export. Streamlit and
the CLI are thin delivery layers over the same service.

