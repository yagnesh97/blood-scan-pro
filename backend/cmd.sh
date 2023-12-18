#!/bin/bash
if [ $1 == "start" ];
then
    poetry run python -m app.main
elif [ $1 == "format" ];
then
    poetry run python -m ruff format app/
    poetry run python -m ruff check --fix app/
elif [ $1 == "test" ];
then
    poetry run coverage run --source app/ -m pytest --disable-warnings
    poetry run coverage xml
    poetry run coverage html
    poetry run coverage report -m
else
    echo "Command not found"
fi