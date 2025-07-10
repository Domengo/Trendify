#!/bin/sh
export PATH="$HOME/.local/bin:$PATH"

#poetry install
source .venv/bin/activate
export FLASK_DEBUG=1
if ! grep -q "$PATH" /home/user/.bashrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/user/.bashrc
fi

export FLASK_APP=src
flask run