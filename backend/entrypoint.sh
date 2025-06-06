#!/bin/bash

perform_migrations() {
    echo "Applying database migrations..."
    if python manage.py makemigrations; then
        echo "Migrations created successfully"
    else
        echo "Error creating migrations" >&2
        exit 1
    fi

    if python manage.py migrate; then
        echo "Migrations applied successfully"
    else
        echo "Error applying migrations" >&2
        exit 1
    fi
}

collect_static_files() {
    echo "Collecting static files..."
    if python manage.py collectstatic --noinput; then
        echo "Static files collected successfully"
    else
        echo "Error collecting static files" >&2
        exit 1
    fi
}

load_fixtures() {
    local fixture_file="dump/init.json"
    echo "Loading fixtures from $fixture_file..."

    if [ -f "$fixture_file" ]; then
        if python manage.py loaddata "$fixture_file"; then
            echo "Fixtures loaded successfully"
        else
            echo "Error loading fixtures" >&2
            exit 1
        fi
    else
        echo "Fixture file $fixture_file not found, skipping..." >&2
    fi
}

main() {
    perform_migrations
    collect_static_files
    load_fixtures

    echo "Starting Gunicorn server..."
    exec gunicorn --bind 0.0.0.0:8000 --timeout 90 foodgram.wsgi
}

main