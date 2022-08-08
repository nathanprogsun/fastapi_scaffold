#! /usr/bin/env bash
set -e

celery worker -A src.worker -l info -Q main-queue -c 1
