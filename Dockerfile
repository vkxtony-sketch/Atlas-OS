# Atlas OS - Local-first Python runtime.
#
# Fixes the prior CMD escaping bug: previously the literal "\\\"build a sample
# goal\\\"" would be passed as multiple args to python, breaking the default
# launch. We now use an ENTRYPOINT for `python main.py` plus a default CMD
# that supplies a single, properly-joined argument.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install deps in their own layer for caching.
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the project.
COPY . /app

# ENTRYPOINT runs `python main.py` and accepts any goal as $goal.
ENTRYPOINT ["python", "main.py"]

# Default goal if none provided. Use the JSON-array form so the entire
# string is a single argv entry — no shell, no quote escape problems.
CMD ["build a sample goal"]
