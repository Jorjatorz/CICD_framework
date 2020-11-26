FROM python:3.8

WORKDIR vcs/

COPY requirements* requirements/

RUN python3 -m venv venv_tap
RUN /bin/bash -c "source venv_tap/bin/activate && pip install -r requirements/requirements_tap.txt && deactivate"

RUN python3 -m venv venv_target
RUN /bin/bash -c "source venv_target/bin/activate && pip install -r requirements/requirements_target.txt && deactivate"

RUN pip install -r requirements/requirements.txt

COPY src/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]