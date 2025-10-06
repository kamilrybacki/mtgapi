#!/bin/sh
set -eu
curl -fsS http://127.0.0.1:8000/docs > /dev/null || exit 1
