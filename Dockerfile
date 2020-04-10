FROM python:3

RUN pip install lastversion
RUN pip install gitpython

COPY shop-extensions.json /usr/bin/shop-extensions.json
COPY src/main.py /usr/bin/main.py
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
