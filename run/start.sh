#! /usr/bin/env sh

# Exit on error
set -e

cd /app
echo "before execute python init.py"
python /app/init.py
echo "end execute python init.py"

# Start Supervisor, with Nginx and uWSGI
echo "before start supervisord"
exec /usr/local/bin/supervisord -c /app/run/supervisord.conf
echo "end start supervisord"