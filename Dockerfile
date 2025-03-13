FROM python:3.11.2-bullseye

ARG USER
ARG PASS
RUN echo "machine gitlab.com \
         "    login ${USER} \
         "    password ${PASS}" > /root/.netrc
RUN chown root ~/.netrc
RUN chmod 0600 ~/.netrc

RUN pip3 install --upgrade setuptools wheel
RUN pip3 install --upgrade pip

COPY . .
RUN pip3 config set global.extra-index-url https://gitlab.com/api/v4/groups/71493013/-/packages/pypi/simple
RUN pip3 install .

ENTRYPOINT ["python", "main.py"]