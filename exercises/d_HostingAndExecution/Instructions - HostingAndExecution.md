# Delivery And Hosting
In this phase, we will deploy the model for consumption by other users. We will start by deploying the model as a REST API endpoint and verify that it is running properly. We will then deploy a dashboard via a Streamlit application that calls the REST endpoint. We will finally deploy a Domino Launcher that allows users to interact with Domino through a web form.

## Exercise Instructions

### Deploy the model as a REST API endpoint

1. Click "Models" (Left-hand column) and open the model registered at the end of Exercise 3.

2. Publish that model version as an endpoint. Select a hardware tier (Small is sufficient) and leave the remaining settings as default.

3. Wait for the endpoint to build and start. This takes a few minutes — it is provisioning a live serving container.

4. Open the endpoint's detail page and copy the **endpoint URL** and the **auth token**. The token is used as both the username and password for basic authentication.

### Deploy the web app

5. Set the endpoint URL and token as environment variables so the app can reach the model (Project → Settings → Environment Variables):
   - `xgboost_endpoint` — the endpoint URL
   - `xgboost_auth` — the auth token

   The app also supports `adaboost_endpoint`/`adaboost_auth` and `gaussiannb_endpoint`/`gaussiannb_auth` if you deploy endpoints for those models too. Any model selected in the app without a configured endpoint falls back to a simple built-in heuristic rather than calling a model.

6. Publish `app.py` as a Domino App, using `app.sh` as the entry point.

7. Open the published app, fill in a simulated transaction, select the model, and click "Predict Fraud Risk".

8. Confirm the returned score came from the endpoint rather than the built-in fallback.

### Deploy a Launcher

9. Create a Domino Launcher pointing at one of the training scripts, so a non-technical user can trigger it from a web form.

This concludes the "4. Delivery & Hosting" section of the workshop.

## New Domino Concepts

**Model Endpoints:**
> Model Endpoints are REST API services that automatically deploy trained models as scalable, production-ready APIs with built-in load balancing, monitoring, and versioning capabilities. This enables data scientists to instantly serve predictions to applications and systems without writing deployment code or managing infrastructure, while IT maintains governance and security controls.

**Hosted Applications:**
> Hosted Applications allow users to deploy and share interactive web applications (built with frameworks like Streamlit, Dash, or Flask) directly from their Domino projects with automatic scaling and authentication. This empowers data scientists to create self-service analytics tools and model interfaces for business users without requiring web development expertise or separate hosting infrastructure.

**Domino Launchers:**
> Domino Launchers are customizable, self-service interfaces that allow business users to execute pre-configured data science workflows or models by simply filling out a form, without needing access to code or the full Domino platform. This democratizes access to data science outputs by enabling stakeholders to run analyses, generate reports, or get predictions on-demand while data scientists maintain control over the underlying logic and parameters.
