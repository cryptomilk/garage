# Car Connectivity Container Setup

A containerized solution for connecting to your car's API and visualizing data
with Grafana.

## Supported Car Brands

- Audi
- Seat/Cupra
- Skoda
- Volkswagen
- Volvo
- Tronity (multi-brand support)

## Prerequisites

- Podman and podman-compose installed
- Python 3 (for configuration setup)

## Quick Start

### 1. Create Configuration

Run the interactive configuration script to set up your car connector and
credentials:

```bash
./create_config.py
```

The script will prompt you for:
- **Connector type**: Choose your car brand
- **Car API credentials**: Username/password (or client_id/client_secret for
  Tronity)
- **Polling interval**: How often to fetch data from your car (in seconds)
- **WebUI credentials**: Username and password for the web interface
- **Grafana credentials**: Admin username and password for Grafana

This creates two files:
- `config/carconnectivity_config.json` - Car connector and plugin configuration
- `.env` - Grafana admin credentials

### 2. Start Services

Start all services using podman-compose:

```bash
podman-compose -p carconnect up
```

Options:
- Add `-d` to run in detached mode (background):
  `podman-compose -p carconnect up -d`
- View logs: `podman-compose -p carconnect logs -f`

### 3. Stop Services

```bash
podman-compose -p carconnect down
```

## Available Interfaces

Once the services are running, you can access:

| Interface | URL | Port | Description |
|-----------|-----|------|-------------|
| **WebUI** | http://localhost:4000 | 4000 | Car connectivity web interface (login with WebUI credentials) |
| **Grafana** | http://localhost:3000 | 3000 | Data visualization dashboard (login with Grafana credentials) |

## Services

### carconnectivity
- Main service that connects to your car's API
- Polls data at configured intervals
- Stores data in SQLite database
- Provides WebUI for monitoring

### grafana
- Visualization and dashboard platform
- Connects to the carconnectivity database
- Pre-configured to access car data
- Accessible on port 3000

## Data Persistence

The following volumes are created for persistent data:
- `carconnectivity-data`: Stores the SQLite database and car data
- `grafana-data`: Stores Grafana dashboards and settings

## Configuration Details

### Polling Intervals

Default polling intervals by connector type:
- **VW/Skoda/Audi/Seat/Volvo**: 180 seconds (3 minutes)
- **Tronity**: 60 seconds (1 minute)

You can customize these during configuration setup.

### Log Levels

The default log level is set to `error`. To change it, edit
`config/carconnectivity_config.json` and modify the `log_level` field.
Available options:
- `debug`
- `info`
- `warning`
- `error`

### Backup Files

The configuration script automatically creates backups:
- Previous configs: `config/carconnectivity_config.json.backup_YYYYMMDD_HHMMSS`
- Previous .env files: `.env.backup_YYYYMMDD_HHMMSS`

## Troubleshooting

### View Logs

```bash
# All services
podman-compose -p carconnect logs -f

# Specific service
podman-compose -p carconnect logs -f carconnectivity
podman-compose -p carconnect logs -f grafana
```

### Restart Services

```bash
podman-compose -p carconnect restart
```

### Rebuild Containers

If you've made changes to Containerfiles:

```bash
podman-compose -p carconnect up --build
```

### Reset Everything

To start fresh (WARNING: deletes all data):

```bash
podman-compose -p carconnect down -v
```

Then recreate your configuration and start again.

## Network

Services communicate via a dedicated bridge network
(`carconnectivity-network`), allowing secure inter-container communication.
