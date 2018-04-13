#!/bin/bash
gunicorn -k flask_sockets.worker app:app
