FROM apify/actor-python:3.14
COPY --chown=apify:apify requirements.txt ./
RUN pip install -r requirements.txt && pip freeze
COPY --chown=apify:apify . ./
RUN python -m compileall -q steam_price_drop/
CMD ["python", "-m", "steam_price_drop"]
