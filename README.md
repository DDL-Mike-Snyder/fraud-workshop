# Fraud detection workshop

Step-by-step instructions for the Domino fraud-detection workshop: prepare the data, run the
model as a Job, inspect the results in Experiments, register the model, publish an endpoint and
deploy the Streamlit app. Steps 9-10 add two open-model agents on a GPU (a chat agent that
simulates transactions and a LoRA fine-tuned fraud scorer) in a second **Agent** tab.

- `fraud-workshop-guide.html`: the workshop guide. Open it in a browser. Also published as a
  private Claude artifact: https://claude.ai/artifact/AmfQRdGuyB4uTA4zgwUNqb
- `support/`: zip files that support the modeling exercise (`fraud-workshop-data.zip`,
  `fraud-workshop-code.zip`).

The code zip now includes `exercises/f_OpenModelAgents/` (fine-tuning Job, vLLM launcher, both agents, the Agent tab),
`.setup/Dockerfile.llm` (GPU environment) and a Trad ML / Agent tabbed `app.py`. `app.sh` is unchanged apart from one line
that starts the model servers.
