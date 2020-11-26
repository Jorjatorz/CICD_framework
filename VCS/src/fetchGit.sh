#!/bin/bash
venv_tap/bin/tap-github --config config.json --properties properties.json | venv_target/bin/target-postgres --config singer-target-postgres-config.json
