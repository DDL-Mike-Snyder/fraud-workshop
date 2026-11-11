# Domino Compute Environment Setup
Make the below changes to the Domino compute environment for the workshop.
Leave all other entries as Default

### Name:
```
Fraud-Detection-Workshop
```

### Base Environment / Image:

Select:
```
Start from an existing environment
```
From:
```
Domino Standard Environment Py3.10 R4.5   (or the Py3.12 equivalent)
```

Pick the platform's own environment (the Global, Default one) rather than typing a
custom image tag. The original version of this doc pinned a specific registry tag
(`quay.io/domino/domino-standard-environment:ubuntu22-py3.10-r4.5-domino6.1-standard`
— note the `domino6.1` in the tag). If you're deploying on a different Domino version,
that tag may not match what's actually running there. Starting from the platform's own
already-provisioned Standard Environment sidesteps that mismatch entirely.

**Use a Python 3.12 base.** Domino's model-serving harness still calls
`configparser.SafeConfigParser`, which Python 3.12 removed, so without the last
instruction in the Dockerfile an Exercise 4 endpoint fails to start with
`AttributeError: module 'configparser' has no attribute 'SafeConfigParser'` and
`*** no app loaded. GAME OVER ***`. That instruction restores the alias and is verified
working. It writes to a Python 3.12 site-packages path, so on a Python 3.10 base remove
it - 3.10 still has `SafeConfigParser` and does not need it. If your organisation
maintains its own Standard Environment (for example one carrying internal
package-repository settings), start from that.

### Description
```
Fraud Detection Workshop
Based on a Domino Standard Environment (Py3.10 or Py3.12)
Jupyter, Jupyterlab, VSCode, Rstudio
```

### Visibility
```
Globally Accessible
```

### Additional Docker File Instructions:
```
# Install uWSGI pre-requisites
USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add missing library for uWSGI
ARG LDFLAGS=-fno-lto
ENV LDFLAGS=-fno-lto
ENV PYTHONPATH="${PYTHONPATH}:/mnt/code:/mnt"

# Install Flask & uWSGI
# The nbclient/nbconvert version caps that used to be here were dropped: nothing in the
# workshop imports them, and on a Py3.12 base they downgrade the base image's working
# Jupyter stack (nbconvert 7.x -> 6.5.4, mistune 3.x -> 0.8.4).
# ydata_profiling is left unpinned on purpose - any release from 4.7 up works, so an
# internal mirror can serve whatever it has. It's only used for the EDA report in
# Exercise B, which the script skips cleanly if the package isn't installed at all.
# Note that 4.7.x pins numpy<2 and will downgrade numpy/scipy/matplotlib on a Python
# 3.12 base; the workshop is verified to run on that combination.
RUN pip install --no-cache-dir "setuptools<81" Flask Flask-Compress Flask-Cors uwsgi six prometheus-client ydata_profiling streamlit st-pages streamlit-extras "lxml[html_clean]"

# Switch back to the standard non-root user - required for Model API builds, which
# run Domino's own build steps as whatever user the image ends on. Leaving this as
# root causes those steps to fail with a permission error.
USER ubuntu
```

### Plugable Workspace Tools
```
jupyter:
  title: "Jupyter (Python, R, Julia)"
  iconUrl: "/assets/images/workspace-logos/Jupyter.svg"
  start: [ "/opt/domino/workspaces/jupyter/start" ]
  supportedFileExtensions: [ ".ipynb" ]
  httpProxy:
    port: 8888
    rewrite: false
    internalPath: "/{{ownerUsername}}/{{projectName}}/{{sessionPathComponent}}/{{runId}}/{{#if pathToOpen}}tree/{{pathToOpen}}{{/if}}"
    requireSubdomain: false
jupyterlab:
  title: "JupyterLab"
  iconUrl: "/assets/images/workspace-logos/jupyterlab.svg"
  start: [  "/opt/domino/workspaces/jupyterlab/start" ]
  httpProxy:
    internalPath: "/{{ownerUsername}}/{{projectName}}/{{sessionPathComponent}}/{{runId}}/{{#if pathToOpen}}tree/{{pathToOpen}}{{/if}}"
    port: 8888
    rewrite: false
    requireSubdomain: false
vscode:
  title: "vscode"
  iconUrl: "/assets/images/workspace-logos/vscode.svg"
  start: [ "/opt/domino/workspaces/vscode/start" ]
  httpProxy:
    port: 8888
    requireSubdomain: false
rstudio:
  title: "RStudio"
  iconUrl: "/assets/images/workspace-logos/Rstudio.svg"
  start: [ "/opt/domino/workspaces/rstudio/start" ]
  httpProxy:
    port: 8888
    requireSubdomain: false
```
Build It
