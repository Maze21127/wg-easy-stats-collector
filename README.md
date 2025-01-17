# wg-easy stats collector
Collecting transfer data from wg-easy and store to clickhouse


# Install
```bash
poetry install --no-root --with dev 
```

# Test
> requires installed docker for testcontainers
```bash
poetry run pytest .
```

# Launch

## Start Clickhouse
> requires installed docker
```bash
docker run -d --name ch -p 9000:9000 -p 8443:8443 -p 8123:8123 clickhouse/clickhouse-server:23.1-alpine
```
## Create .env file
```
WG_URL="http://localhost:8080"
WG_PASSWORD="password"
CH_DSN="clickhouse://default:default@localhost:9000/default"
```

# Add to cron (every 30 mins)
```bash
cat <(crontab -l) <(echo "*/30 * * * * cd $(pwd) && poetry run python main.py >> $(pwd)/cron_log.txt 2>&1") | crontab - 
```