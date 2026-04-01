# Logistics Intelligence Platform

A **Last-Mile Logistics Control Tower** that combines real-time live operations with Big Data analytics. Think Uber's driver tracking meets Datadog's observability dashboards — built for monitoring, simulating, and analyzing delivery fleets across 10 Indian cities.

---

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [The Live Tracking Dashboard](#the-live-tracking-dashboard)
- [The Analytics Dashboard](#the-analytics-dashboard)
- [Backend Deep Dive](#backend-deep-dive)
  - [Database Models](#database-models)
  - [API Endpoints](#api-endpoints)
  - [Real-Time Simulation Engine](#real-time-simulation-engine)
  - [WebSocket Protocol](#websocket-protocol)
- [Big Data Pipeline](#big-data-pipeline)
  - [HDFS Export](#1-hdfs-export)
  - [MapReduce Cleaning](#2-mapreduce-cleaning)
  - [PySpark Analytics](#3-pyspark-analytics-4-jobs)
- [Docker Infrastructure](#docker-infrastructure)
- [Frontend Deep Dive](#frontend-deep-dive)
  - [Pages & Routing](#pages--routing)
  - [Components](#components)
  - [WebSocket Client](#websocket-client)
  - [API Client](#api-client)
- [Supported Cities](#supported-cities)
- [Running Tests](#running-tests)
- [Commands Reference](#commands-reference)

---

## What This Project Does

This platform simulates and monitors a last-mile delivery fleet in real time. Here is the complete flow:

1. **Seed**: On startup, the system seeds a SQLite database with 3 delivery zones, 15 drivers, and 500 orders for a selected Indian city.
2. **Simulate**: A background loop moves drivers along real road routes (fetched from OSRM) every 3 seconds. Drivers pick up orders, deliver them, and get reassigned.
3. **Broadcast**: Every tick, all 15 driver positions (with risk scores, ETAs, SLA deadlines) are broadcast over WebSocket to connected frontends.
4. **Visualize**: A Next.js dashboard shows drivers moving on an OpenStreetMap, with route overlays, zone heatmaps, risk escalation toasts, and live KPI stats.
5. **Analyze**: Completed orders can be exported to HDFS, cleaned via a MapReduce pipeline, and processed by 4 PySpark jobs to generate zone analytics, driver rankings, delay-risk predictions, and route efficiency scores.
6. **Dashboard**: An analytics page visualizes Spark results with bar charts, line charts, driver rankings, and smart risk alerts.

---

## Architecture Overview

```
                        ┌──────────────────────────────┐
                        │     Next.js Frontend         │
                        │     (localhost:3000)          │
                        │                              │
                        │  / ─ Live Tracking Dashboard  │
                        │  /analytics ─ Big Data Page   │
                        └──────────┬───────────────────┘
                                   │
                          REST + WebSocket
                                   │
                        ┌──────────▼───────────────────┐
                        │     FastAPI Backend           │
                        │     (localhost:8000)          │
                        │                              │
                        │  Routers: orders, drivers,    │
                        │  zones, websocket, pipeline,  │
                        │  analytics, cities            │
                        │                              │
                        │  Services: simulation,        │
                        │  routing (OSRM), hdfs_export  │
                        │                              │
                        │  Database: SQLite             │
                        │  (logistics.db)               │
                        └───┬──────────┬───────────────┘
                            │          │
                  ┌─────────▼──┐   ┌───▼───────────────┐
                  │   OSRM     │   │  Docker Cluster    │
                  │  (Public   │   │                    │
                  │   API)     │   │  HDFS (NameNode +  │
                  │            │   │       DataNode)    │
                  └────────────┘   │  YARN (RM + NM)   │
                                   │  MapReduce History │
                                   │  Spark Master +    │
                                   │       Worker       │
                                   └────────────────────┘
```

**Data Pipeline Flow:**
```
SQLite ──export──▶ HDFS /raw/ ──MapReduce──▶ HDFS /cleaned/ ──Spark──▶ HDFS /results/
                                                                            │
                                                    FastAPI reads ◀─────────┘
                                                         │
                                                    Frontend renders
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 16, React 19, TypeScript | App framework, UI |
| Styling | Tailwind CSS 4 | Dark-mode enterprise UI |
| Maps | React-Leaflet 5 + OpenStreetMap | Interactive map with driver markers |
| Charts | Recharts 3 | Bar charts, line charts on analytics page |
| Backend | FastAPI, Uvicorn | REST API + WebSocket server |
| Database | SQLite + SQLAlchemy | Orders, drivers, zones, daily snapshots |
| Real-time | WebSockets | Live driver position broadcast every 3s |
| Routing | OSRM (public API) | Real road-following routes for drivers |
| Big Data | Apache Hadoop 3 (HDFS + YARN) | Distributed storage and job scheduling |
| Processing | MapReduce (Python streaming) | Data validation and cleaning |
| Analytics | Apache Spark 3.5 (PySpark) | 4 analytical jobs on delivery data |
| Infrastructure | Docker Compose | 7-container Hadoop/Spark cluster |

---

## Project Structure

```
bdashit/
├── CLAUDE.md                        # AI assistant directives
├── README.md                        # This file
├── me.cpp                           # Placeholder
│
├── backend/
│   ├── requirements.txt             # Python dependencies
│   ├── pytest.ini                   # Test config
│   ├── logistics.db                 # SQLite database (auto-generated)
│   │
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point, lifespan, city endpoints
│   │   ├── database.py              # SQLAlchemy engine + session factory
│   │   ├── models.py                # ORM models: Zone, Driver, Order, DailySnapshot
│   │   ├── schemas.py               # Pydantic response models
│   │   ├── cities.py                # Config for 10 Indian cities (zones, coords)
│   │   ├── seed.py                  # Database seeder (zones, drivers, orders, snapshots)
│   │   │
│   │   ├── routers/
│   │   │   ├── orders.py            # Order CRUD + live stats + route lookup
│   │   │   ├── drivers.py           # Driver listing
│   │   │   ├── zones.py             # Zone listing + heatmap data
│   │   │   ├── websocket.py         # WebSocket server + broadcast
│   │   │   ├── pipeline.py          # HDFS export + MapReduce execution
│   │   │   └── analytics.py         # Spark job submission + result reading
│   │   │
│   │   └── services/
│   │       ├── simulation.py        # Driver movement engine (core loop)
│   │       ├── routing.py           # OSRM route fetching + caching
│   │       └── hdfs_export.py       # SQLite → HDFS CSV export
│   │
│   ├── mapreduce/
│   │   ├── mapper.py                # Hadoop streaming mapper (validation)
│   │   └── reducer.py               # Hadoop streaming reducer (aggregation)
│   │
│   ├── spark_jobs/
│   │   ├── zone_analytics.py        # Zone-level delivery metrics
│   │   ├── driver_utilization.py    # Per-driver performance scoring
│   │   ├── route_efficiency.py      # Zone-driver route quality
│   │   └── delay_prediction.py      # Delay risk scoring by zone + hour
│   │
│   └── tests/
│       └── test_api.py              # 11 tests (API + WebSocket + simulation)
│
├── frontend/
│   ├── package.json                 # Next.js 16, React 19, Leaflet, Recharts
│   ├── next.config.ts               # API proxy rewrite to backend
│   ├── tsconfig.json                # TypeScript config
│   ├── postcss.config.mjs           # Tailwind PostCSS plugin
│   │
│   └── src/
│       ├── app/
│       │   ├── layout.tsx           # Root layout (dark theme, fonts)
│       │   ├── globals.css          # Tailwind + custom animations
│       │   ├── page.tsx             # Home: Live Tracking Dashboard
│       │   │
│       │   ├── analytics/
│       │   │   └── page.tsx         # Analytics: Big Data Dashboard
│       │   │
│       │   └── components/
│       │       ├── MapView.tsx           # Leaflet map container
│       │       ├── DriverMarker.tsx      # Animated driver icons
│       │       ├── DestinationMarkers.tsx # Delivery destination circles
│       │       ├── RouteOverlay.tsx       # Route polyline (completed/remaining)
│       │       ├── ZoneHeatmapLayer.tsx   # Zone load visualization
│       │       ├── MapLegend.tsx          # Map legend (risk colors)
│       │       ├── OrderSidebar.tsx       # Fleet status sidebar
│       │       ├── LiveStatsBar.tsx       # KPI metrics bar
│       │       ├── LiveToasts.tsx         # Risk escalation notifications
│       │       ├── ZoneDelayChart.tsx     # Recharts bar chart
│       │       ├── DriverRankings.tsx     # Top/bottom 5 drivers
│       │       ├── SmartAlerts.tsx        # Risk alert cards
│       │       └── HistoricalComparison.tsx # Week-over-week line chart
│       │
│       └── lib/
│           ├── api.ts               # REST API client + TypeScript interfaces
│           └── websocket.ts         # WebSocket singleton + pub-sub
│
├── docker/
│   ├── docker-compose.yml           # 7-service Hadoop/Spark cluster
│   ├── hadoop/
│   │   ├── core-site.xml            # HDFS default FS config
│   │   ├── hdfs-site.xml            # Replication, data dirs
│   │   ├── mapred-site.xml          # YARN framework, history server
│   │   ├── yarn-site.xml            # Resource limits (2GB, 2 cores)
│   │   └── hadoop.env               # Environment variables
│   └── spark/
│       └── spark-defaults.conf      # Spark master, memory, HDFS integration
│
└── docs/
    ├── PLAN.md                      # 6-phase implementation roadmap
    └── v2.md                        # V2 feature enhancements plan
```

---

## Getting Started

### Prerequisites

- **Node.js** (v18+)
- **Python** (3.10+)
- **Docker** and **Docker Compose**

### 1. Start the Hadoop/Spark cluster

```bash
cd docker
docker compose up -d
```

This spins up 7 containers: NameNode, DataNode, ResourceManager, NodeManager, HistoryServer, Spark Master, Spark Worker. Wait for health checks to pass (~30s).

**Verify:**
- HDFS Web UI: http://localhost:9870
- YARN Web UI: http://localhost:8088
- Spark Master UI: http://localhost:8080

### 2. Start the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On startup, the backend:
- Creates SQLite tables
- Seeds 3 zones, 15 drivers, 500 orders for Delhi (default city)
- Starts the background simulation loop (moves drivers every 3s)
- Prefetches OSRM routes for active deliveries

**API available at:** http://localhost:8000  
**API docs (Swagger):** http://localhost:8000/docs

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

**Dashboard available at:** http://localhost:3000

---

## The Live Tracking Dashboard

**Route:** `/` (home page)

This is the main operational view. Here is everything it shows:

### Header Bar
- **Logo** and app title
- **City Selector**: Dropdown to switch between 10 Indian cities. Switching re-seeds the entire database with city-specific coordinates.
- **Search**: Type a tracking number to find a driver on the map. The map flies to the driver and highlights them in the sidebar.
- **Status Badges**: Live count of drivers by risk — green (on track), yellow (SLA < 20min), red (SLA < 10min), gray (idle).
- **Heatmap Toggle**: Shows/hides zone load overlay on the map.
- **LIVE Indicator**: Green dot when WebSocket is connected.
- **Analytics Link**: Navigate to the analytics page.

### Live Stats Bar
Five KPI metrics refreshed every 10 seconds:
- **Delivered Today**: Orders delivered since midnight
- **Avg Delay**: Average delay in minutes
- **Success Rate**: Percentage of on-time deliveries
- **Active**: In-transit orders
- **Pending**: Waiting for assignment

### Map (Left Side)
- **OpenStreetMap** tiles via React-Leaflet
- **Driver Markers**: Colored circles with driver initials. Colors = risk level (green/yellow/red). Idle drivers are faded. Markers animate smoothly between positions (2.5s transition). Clicking a marker shows a popup with driver name, status, tracking number, zone, risk, ETA, and SLA deadline.
- **Destination Markers**: Red dashed circles at delivery locations for active drivers.
- **Route Overlay** (on driver click): A polyline showing the driver's route — gray dashed line for completed portion, solid blue for remaining. Green circle at pickup, red circle at delivery.
- **Zone Heatmap** (toggleable): Colored circles over each zone center. Green = low load, yellow = moderate, red = overloaded. Tooltip shows active orders, pending orders, available drivers, and load ratio.
- **Legend**: Bottom-left corner explaining all marker types.

### Fleet Sidebar (Right Side)
- Lists all 15 drivers sorted by risk (red first, then yellow, green, idle last)
- Each card shows: driver name, status badge, risk dot, tracking number, zone, SLA deadline, ETA
- Late ETAs shown in red, on-time in blue
- Clicking a driver selects them and fetches their route
- Search highlight pulses with a blue animation

### Risk Escalation Toasts
- When a driver's risk level worsens (green → yellow, or anything → red), a toast notification slides in from the bottom-right
- Shows driver name, tracking number, and risk change (e.g., "green → red")
- Auto-dismisses after 5 seconds

---

## The Analytics Dashboard

**Route:** `/analytics`

This page runs the full big data pipeline and visualizes results.

### Pipeline Execution
A single "Run Full Pipeline" button triggers this sequence:
1. **Export to HDFS** — Writes completed/delayed orders from SQLite to CSV on HDFS (`/logistics/raw/delivery_logs_YYYYMMDD.csv`)
2. **Run MapReduce** — Validates and cleans the data (mapper validates coords, driver IDs, delay values; reducer aggregates by zone). Output: `/logistics/cleaned/run_YYYYMMDD/part-00000`
3. **Run 4 Spark Jobs** — Submits each PySpark job to the Spark cluster:
   - `zone_analytics`
   - `driver_utilization`
   - `route_efficiency`
   - `delay_prediction`
4. **Refresh Dashboard** — Reads Spark results from HDFS and renders charts

### Visualizations

**Summary Cards** (top row):
- Total Deliveries, Average Delay, Zones Tracked, High-Risk Slots

**Zone Delay Chart** (Recharts bar chart):
- Total delay minutes per zone (A, B, C)
- Below: per-zone cards with delivery count, avg delay, delivery rate

**Smart Alerts** (risk predictions):
- Shows HIGH and MEDIUM risk slots by zone + hour
- Badge counts for each risk level
- Each alert: zone, hour (e.g., "2 PM"), delivery count, avg/max delay, delayed count

**Driver Rankings** (two-column layout):
- **Top 5 Performers**: Highest on-time percentage, with progress bars
- **Bottom 5 Performers**: Lowest on-time percentage, with avg delay shown
- Each entry: driver ID, on-time %, total deliveries, primary zone, rate

**Historical Comparison** (Recharts line chart):
- Compares current 7-day period vs previous 7-day period
- Toggle between "Avg Delay" and "Total Deliveries" metrics
- Optional zone filter dropdown
- Data comes from DailySnapshot table (SQLite), not HDFS — always available even before pipeline runs

---

## Backend Deep Dive

### Database Models

**Zone** — Delivery zones within a city
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| name | String (unique) | "A", "B", or "C" |
| center_lat / center_lng | Float | Zone center coordinates |
| radius_km | Float | Zone radius in kilometers |

**Driver** — Delivery drivers
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| name | String | Driver's name |
| current_lat / current_lng | Float | Live GPS position |
| status | String | "idle", "en_route", or "delivering" |
| assigned_zone_id | FK → Zone | Which zone the driver operates in |

**Order** — Delivery orders
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| tracking_number | String (unique) | e.g., "TRK-000001" |
| pickup_lat / pickup_lng | Float | Pickup coordinates |
| delivery_lat / delivery_lng | Float | Delivery coordinates |
| zone_name | FK → Zone.name | Which zone this order belongs to |
| status | String | "pending", "in_transit", "delivered", "delayed" |
| driver_id | FK → Driver | Assigned driver (nullable) |
| created_at | DateTime | Order creation time |
| delivered_at | DateTime | Delivery completion time (nullable) |
| sla_deadline | DateTime | When the delivery must be completed by |
| delay_minutes | Integer | How many minutes late (0 if on-time) |

**DailySnapshot** — Historical daily aggregates
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| snapshot_date | Date | Which day |
| zone_name | String | Which zone |
| total_deliveries | Integer | Deliveries completed that day |
| total_delayed | Integer | How many were late |
| avg_delay_minutes | Float | Average delay |
| on_time_pct | Float | On-time delivery percentage |

### API Endpoints

#### Cities
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/cities` | List all 10 supported cities |
| GET | `/api/cities/current` | Detect currently active city |
| POST | `/api/cities/{city_key}` | Switch city (re-seeds database) |

#### Orders
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/orders?limit=20&offset=0` | List orders with pagination |
| GET | `/api/orders/{order_id}` | Get single order details |
| GET | `/api/orders/{order_id}/route` | Get active route waypoints |
| GET | `/api/orders/stats/live` | Live KPI stats (delivered today, avg delay, success rate, active, pending) |

#### Drivers
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/drivers` | List all 15 drivers |

#### Zones
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/zones` | List all 3 zones |
| GET | `/api/zones/heatmap` | Zone load data (active orders, pending, available drivers, load ratio, intensity color) |

#### Pipeline (Big Data)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/export-to-hdfs` | Export orders from SQLite to HDFS CSV |
| POST | `/api/run-mapreduce` | Run mapper → sort → reducer on HDFS data |

#### Analytics (Spark Results)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/run-spark/{job_name}` | Submit a PySpark job (zone_analytics, driver_utilization, route_efficiency, delay_prediction) |
| GET | `/api/analytics/zones` | Read zone analytics results |
| GET | `/api/analytics/drivers` | Read driver utilization results |
| GET | `/api/analytics/routes` | Read route efficiency results |
| GET | `/api/analytics/delay-risk` | Read delay prediction results |
| GET | `/api/analytics/historical?days=7&zone=A` | Historical comparison (current vs previous period) |

#### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |

#### WebSocket
| Path | Description |
|------|-------------|
| `ws://localhost:8000/ws/tracking` | Real-time driver position stream |

### Real-Time Simulation Engine

The simulation engine (`backend/app/services/simulation.py`) is the heart of the live operations. Here is how it works:

**Startup:**
1. On app startup, `prefetch_all_routes()` fetches OSRM road routes for up to 15 active orders (one per driver). Remaining orders get straight-line fallback routes.
2. The `simulation_loop()` coroutine starts and runs indefinitely.

**Every 3 Seconds (`_step_drivers`):**
1. Query all `in_transit` orders with their assigned drivers
2. For each order:
   - Get or lazy-fetch the OSRM route
   - Advance the driver to the next waypoint along the route
   - Update the driver's lat/lng in the database
   - If the driver reached the final waypoint:
     - Mark order as `delivered`, set `delivered_at` timestamp
     - Check if the order missed its SLA deadline; if so, set status to `delayed` and compute `delay_minutes`
     - Find the next `pending` order in the same zone
     - If found: assign it to the driver, set driver to `en_route`, fetch the new route
     - If none: set driver to `idle`
3. Collect ALL 15 driver payloads (active + idle) to maintain stable count
4. Broadcast via WebSocket to all connected clients

**Risk Scoring (`_compute_risk`):**
- Calculates distance from driver to delivery using Haversine formula
- Compares remaining distance vs time until SLA deadline
- **Red**: distance > 2km AND time remaining < 10 minutes
- **Yellow**: distance > 1km AND time remaining < 20 minutes
- **Green**: everything else

**Route Caching:**
- OSRM routes are cached in `_route_cache` (dict keyed by order_id)
- Cache is cleared on city switch
- Fallback: if OSRM is unavailable, a straight line with 10 interpolated points is used

### WebSocket Protocol

**Connection:** `ws://localhost:8000/ws/tracking`

**Message format:** JSON array of driver update objects, broadcast every 3 seconds:

```json
[
  {
    "driver_id": 1,
    "driver_name": "Rahul Sharma",
    "lat": 28.6139,
    "lng": 77.2090,
    "status": "en_route",
    "risk": "green",
    "order_id": 42,
    "tracking_number": "TRK-000042",
    "delivery_lat": 28.6200,
    "delivery_lng": 77.2150,
    "zone": "A",
    "sla_deadline": "2026-04-01T15:30:00",
    "eta_minutes": 12.5,
    "eta_time": "2026-04-01T15:22:30"
  },
  ...
]
```

**Frontend behavior:**
- Singleton WebSocket with auto-reconnect (3 second delay)
- Pub-sub pattern: components subscribe to updates, unsubscribe on unmount
- Auto-connects on first subscriber, closes when last subscriber leaves

---

## Big Data Pipeline

The pipeline processes delivery data in 3 stages: Export → Clean → Analyze.

### 1. HDFS Export

**Trigger:** `POST /api/export-to-hdfs`

**What it does:**
- Queries all `delivered` and `delayed` orders from SQLite
- Builds a CSV with columns: `Timestamp, DriverID, Zone, Lat, Lng, Status, DelayTime`
- Pipes the CSV into the namenode Docker container via `docker exec`
- Uploads to HDFS at `/logistics/raw/delivery_logs_YYYYMMDD.csv`

### 2. MapReduce Cleaning

**Trigger:** `POST /api/run-mapreduce`

**Mapper** (`backend/mapreduce/mapper.py`):
- Reads CSV lines from stdin
- Validates each row:
  - Skips header
  - Drops rows with null/empty DriverID
  - Drops rows with coordinates outside India (8-37N, 68-98E)
  - Drops rows with negative delay times
  - Reports validation counters to stderr
- Emits: `Zone\tDriverID,Lat,Lng,Status,DelayTime,Timestamp`

**Reducer** (`backend/mapreduce/reducer.py`):
- Receives mapper output sorted by zone
- Groups records by zone
- Counts deliveries, sums delay, flags anomalies (delay > 60 min)
- Emits cleaned CSV to stdout
- Emits zone summaries to stderr: `#SUMMARY|Zone|count=N|total_delay=M|anomalies=K`

**Pipeline command:**
```
hdfs dfs -cat /input.csv | python mapper.py | sort | python reducer.py > /output/part-00000
```

**Output:** `/logistics/cleaned/run_YYYYMMDD/part-00000`

### 3. PySpark Analytics (4 Jobs)

All jobs read from the cleaned data and write JSON results to HDFS.

#### Zone Analytics (`spark_jobs/zone_analytics.py`)
- **Input:** Cleaned CSV
- **Output:** `/logistics/results/zone_analytics`
- **Metrics per zone:**
  - total_deliveries, avg_delay_min, total_delay_min, delayed_count
  - peak_hour (hour with most deliveries)
  - peak_hour_deliveries, overloaded_hours (hours with >10 deliveries)

#### Driver Utilization (`spark_jobs/driver_utilization.py`)
- **Input:** Cleaned CSV
- **Output:** `/logistics/results/driver_utilization`
- **Metrics per driver:**
  - total_deliveries, avg_delay_min, total_delay_min
  - delivered_count, delayed_count
  - primary_zone, deliveries_per_hour, on_time_pct

#### Route Efficiency (`spark_jobs/route_efficiency.py`)
- **Input:** Cleaned CSV
- **Output:** `/logistics/results/route_efficiency`
- **Metrics per zone + driver combination:**
  - deliveries, avg_delay_min, max_delay_min
  - avg_lat, avg_lng (route center)
  - efficiency_score = `(1 - avg_delay/max_delay) * 100`

#### Delay Prediction (`spark_jobs/delay_prediction.py`)
- **Input:** Cleaned CSV
- **Output:** `/logistics/results/delay_prediction`
- **Metrics per zone + hour:**
  - delivery_count, avg_delay_min, max_delay_min, delayed_count
  - risk_level: HIGH (>10 deliveries AND avg delay >15min), MEDIUM (avg delay >10 OR >8 deliveries), LOW
  - risk_score: 3 (HIGH), 2 (MEDIUM), 1 (LOW)

---

## Docker Infrastructure

The `docker/docker-compose.yml` defines a 7-service cluster on a `logistics-net` bridge network:

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| namenode | apache/hadoop:3 | 9870, 8020 | HDFS NameNode (metadata + coordination) |
| datanode | apache/hadoop:3 | 9864 | HDFS DataNode (actual data storage) |
| resourcemanager | apache/hadoop:3 | 8088 | YARN ResourceManager (job scheduling) |
| nodemanager | apache/hadoop:3 | 8042 | YARN NodeManager (container execution) |
| historyserver | apache/hadoop:3 | 19888 | MapReduce Job History |
| spark-master | apache/spark:3.5.8-python3 | 8080, 7077 | Spark Master (cluster coordinator) |
| spark-worker | apache/spark:3.5.8-python3 | 8081 | Spark Worker (2 cores, 1GB memory) |

**Key configs:**
- HDFS replication factor: 1 (single datanode for dev)
- YARN resources: 2048MB memory, 2 vCores
- Spark driver/executor memory: 512MB each
- All services mount `mapreduce/` and `spark_jobs/` from the host for live code iteration

**Web UIs:**
- HDFS: http://localhost:9870
- YARN: http://localhost:8088
- Spark: http://localhost:8080
- History: http://localhost:19888

---

## Frontend Deep Dive

### Pages & Routing

| Route | File | Description |
|-------|------|-------------|
| `/` | `src/app/page.tsx` | Live Tracking Dashboard — map, sidebar, stats, toasts |
| `/analytics` | `src/app/analytics/page.tsx` | Analytics Dashboard — pipeline, charts, rankings, alerts |

The Next.js config proxies all `/api/*` requests to the backend at `http://127.0.0.1:8000`.

### Components

| Component | File | What It Renders |
|-----------|------|-----------------|
| **MapView** | `components/MapView.tsx` | Leaflet map container with OpenStreetMap tiles, manages all map sub-layers |
| **DriverMarker** | `components/DriverMarker.tsx` | Individual driver marker with colored circle (initials), popup, smooth 2.5s position animation. Teleports (>500m jumps) snap instantly. |
| **DestinationMarkers** | `components/DestinationMarkers.tsx` | Red dashed circles at delivery locations for active drivers |
| **RouteOverlay** | `components/RouteOverlay.tsx` | Route polyline: gray dashed (completed) + solid blue (remaining). Green pickup circle, red delivery circle. |
| **ZoneHeatmapLayer** | `components/ZoneHeatmapLayer.tsx` | Colored circles over zone centers showing load intensity (green/yellow/red). Sticky tooltip with metrics. |
| **MapLegend** | `components/MapLegend.tsx` | Fixed bottom-left legend explaining marker colors and types |
| **OrderSidebar** | `components/OrderSidebar.tsx` | Scrollable driver list sorted by risk. Cards show name, status, tracking number, zone, SLA, ETA. |
| **LiveStatsBar** | `components/LiveStatsBar.tsx` | Horizontal KPI bar: deliveries today, avg delay, success rate, active, pending |
| **LiveToasts** | `components/LiveToasts.tsx` | Bottom-right toast notifications for risk escalations (green→yellow, *→red). Auto-dismiss 5s. |
| **ZoneDelayChart** | `components/ZoneDelayChart.tsx` | Recharts bar chart: total delay minutes per zone + per-zone summary cards |
| **DriverRankings** | `components/DriverRankings.tsx` | Two-column layout: top 5 and bottom 5 drivers by on-time percentage |
| **SmartAlerts** | `components/SmartAlerts.tsx` | HIGH/MEDIUM risk alert cards by zone + hour, sorted by severity |
| **HistoricalComparison** | `components/HistoricalComparison.tsx` | Recharts line chart comparing current week vs last week. Zone filter + metric toggle. |

### WebSocket Client

`src/lib/websocket.ts` — Singleton WebSocket connection manager.

- Connects to `ws://localhost:8000/ws/tracking`
- **Pub-sub pattern**: Call `subscribe(callback)` to receive driver updates, returns an unsubscribe function
- **Auto-reconnect**: Reconnects 3 seconds after disconnect
- **Lifecycle**: Connects on first subscriber, closes when no subscribers remain

### API Client

`src/lib/api.ts` — TypeScript fetch wrappers for all backend endpoints.

**Key interfaces:**
- `DriverUpdate` — Full driver state from WebSocket (id, name, lat, lng, status, risk, order_id, tracking_number, delivery coords, zone, SLA, ETA)
- `CityInfo` — City metadata (key, name, center, zoom)
- `RouteData` — Route waypoints with current progress index
- `ZoneHeatmapData` — Zone load metrics and intensity color
- `LiveStats` — Real-time KPI values
- `HistoricalData` — Current period vs previous period arrays

---

## Supported Cities

The platform supports 10 Indian cities, each with 3 pre-configured delivery zones:

| Key | City | Zones |
|-----|------|-------|
| delhi | Delhi | Connaught Place, Karol Bagh, Lajpat Nagar |
| mumbai | Mumbai | Andheri, Bandra, Dadar |
| bangalore | Bangalore | Koramangala, Whitefield, Indiranagar |
| hyderabad | Hyderabad | Banjara Hills, Madhapur, Secunderabad |
| chennai | Chennai | T. Nagar, Adyar, Anna Nagar |
| kolkata | Kolkata | Park Street, Salt Lake, Howrah |
| pune | Pune | Koregaon Park, Hinjewadi, Kothrud |
| ahmedabad | Ahmedabad | Navrangpura, SG Highway, Maninagar |
| jaipur | Jaipur | MI Road, Malviya Nagar, Vaishali Nagar |
| lucknow | Lucknow | Hazratganj, Gomti Nagar, Aminabad |

Each city seeds: **3 zones**, **15 drivers** (5 per zone), **500 orders**, and **14 days of daily snapshots**.

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

The test suite (`backend/tests/test_api.py`) covers 11 tests:

| Test | What It Validates |
|------|-------------------|
| `test_health` | `/api/health` returns 200 |
| `test_list_orders` | Orders endpoint returns data with correct pagination |
| `test_list_orders_pagination` | Offset-based pagination works |
| `test_get_order` | Single order retrieval |
| `test_get_order_not_found` | Returns 404 for missing orders |
| `test_list_drivers` | Returns exactly 15 drivers |
| `test_list_zones` | Returns exactly 3 zones (A, B, C) |
| `test_websocket_connects` | WebSocket accepts connections |
| `test_simulation_step_produces_payloads` | Simulation generates correct payload structure |
| `test_simulation_positions_change` | Driver positions actually update between ticks |
| `test_simulation_risk_field` | Risk field is present and valid (green/yellow/red) |

---

## Commands Reference

| Command | What It Does |
|---------|--------------|
| `npm run dev` | Start the frontend (http://localhost:3000) |
| `uvicorn app.main:app --reload` | Start the backend (http://localhost:8000) |
| `pytest` | Run the backend test suite |
| `cd docker && docker compose up -d` | Start the Hadoop/Spark cluster |
| `cd docker && docker compose down` | Stop the cluster |
| `cd docker && docker compose down -v` | Stop and remove all data volumes |

---

## Design Decisions

- **No paid APIs**: Uses free OpenStreetMap tiles and the public OSRM routing API. All data is mock-generated.
- **SQLite over Postgres**: Simpler for development. The entire DB re-seeds in <1 second on city switch.
- **OSRM fallback**: If the public OSRM server is slow or down, drivers still move along straight-line interpolated routes.
- **Docker exec for HDFS/Spark**: The backend shells into Docker containers to run HDFS commands and Spark submits, avoiding the need to install Hadoop/Spark locally.
- **Module-level route cache**: Routes are cached in Python dicts rather than Redis, keeping the dependency footprint minimal.
- **Client-side rendering**: All frontend pages use `"use client"` since they depend on WebSocket subscriptions, Leaflet (which needs the DOM), and frequent state updates.
