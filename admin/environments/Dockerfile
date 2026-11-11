# This is a convenience copy of the instructions in ./environment.md. Domino handles
# the base image itself — in the Domino UI, select "Start from an existing
# environment" and pick a Python 3.12 Domino Standard Environment. If your organisation
# maintains its own (e.g. one carrying internal package-repository settings), use that.

# Install uWSGI pre-requisites
USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add missing library for uWSGI
ARG LDFLAGS=-fno-lto
ENV LDFLAGS=-fno-lto
ENV PYTHONPATH="${PYTHONPATH}:/mnt/code:/mnt"

# Install Flask & uWSGI
# ydata_profiling is left unpinned on purpose - any release from 4.7 up works, so an
# internal mirror can serve whatever it has. It's only used for the EDA report in
# Exercise B, which the script skips cleanly if the package isn't installed at all.
RUN pip install --no-cache-dir "setuptools<81" Flask Flask-Compress Flask-Cors uwsgi six prometheus-client ydata_profiling streamlit st-pages streamlit-extras "lxml[html_clean]"

# Restores configparser.SafeConfigParser, which Python 3.12 removed and Domino's
# model-serving harness still calls. Without this, an Exercise 4 endpoint never loads
# its app and the pod restart-loops. SafeConfigParser was only ever a deprecated alias
# for ConfigParser, so this is faithful, and the hasattr guard makes it a no-op once the
# harness is fixed. Note the path below is Python 3.12 specific.
USER root
RUN printf '%s\n' \
  'import configparser' \
  'if not hasattr(configparser, "SafeConfigParser"):' \
  '    class SafeConfigParser(configparser.ConfigParser):' \
  '        def readfp(self, fp, filename=None):' \
  '            return self.read_file(fp, filename)' \
  '    configparser.SafeConfigParser = SafeConfigParser' \
  > /opt/conda/lib/python3.12/site-packages/sitecustomize.py

# Switch back to the standard non-root user - required for Model API builds, which
# run Domino's own build steps (e.g. creating an mlflow directory under /mnt) as
# whatever user the image ends on. Leaving this as root causes those steps to fail
# with a permission error against the expected non-root mount ownership.
USER ubuntu
