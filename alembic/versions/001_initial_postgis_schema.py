"""Initial PostGIS schema for PENELOPE

Revision ID: 001_initial_postgis_schema
Revises: 
Create Date: 2026-11-14 09:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_postgis_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable PostGIS Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. regions table
    op.execute("""
    CREATE TABLE IF NOT EXISTS regions (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        state VARCHAR(60) NOT NULL,
        geom GEOMETRY(MultiPolygon, 4326),
        centroid GEOMETRY(Point, 4326),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
    );
    CREATE INDEX IF NOT EXISTS idx_regions_geom ON regions USING GIST (geom);
    CREATE INDEX IF NOT EXISTS idx_regions_centroid ON regions USING GIST (centroid);
    """)

    # 3. locations table
    op.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id VARCHAR(36) PRIMARY KEY,
        region_id VARCHAR(36) NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
        name VARCHAR(140) NOT NULL,
        type VARCHAR(40) NOT NULL DEFAULT 'village',
        geom GEOMETRY(Point, 4326) NOT NULL,
        elevation_m DOUBLE PRECISION NOT NULL DEFAULT 1500.0,
        population INTEGER NOT NULL DEFAULT 500,
        source VARCHAR(60) NOT NULL DEFAULT 'osm',
        hindi_name VARCHAR(140),
        current_risk_score DOUBLE PRECISION DEFAULT 0.15,
        current_risk_level VARCHAR(20) DEFAULT 'Low',
        slope_degrees DOUBLE PRECISION DEFAULT 18.0,
        river_distance_m DOUBLE PRECISION DEFAULT 250.0,
        capacity_persons INTEGER DEFAULT 200,
        contact_person VARCHAR(80),
        contact_phone VARCHAR(30),
        status VARCHAR(20) DEFAULT 'Ready',
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
    );
    CREATE INDEX IF NOT EXISTS idx_locations_geom ON locations USING GIST (geom);
    CREATE INDEX IF NOT EXISTS idx_locations_region_id ON locations (region_id);
    CREATE INDEX IF NOT EXISTS idx_locations_type ON locations (type);
    """)

    # 4. grid_cells table
    op.execute("""
    CREATE TABLE IF NOT EXISTS grid_cells (
        id VARCHAR(36) PRIMARY KEY,
        region_id VARCHAR(36) NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
        geom GEOMETRY(Polygon, 4326) NOT NULL,
        centroid GEOMETRY(Point, 4326) NOT NULL,
        elevation_m DOUBLE PRECISION NOT NULL DEFAULT 1200.0,
        slope_deg DOUBLE PRECISION NOT NULL DEFAULT 15.0,
        aspect DOUBLE PRECISION NOT NULL DEFAULT 180.0,
        twi DOUBLE PRECISION NOT NULL DEFAULT 6.5,
        flow_accum DOUBLE PRECISION NOT NULL DEFAULT 120.0,
        dist_to_river_m DOUBLE PRECISION NOT NULL DEFAULT 200.0,
        landcover VARCHAR(60) NOT NULL DEFAULT 'forest',
        res_m DOUBLE PRECISION NOT NULL DEFAULT 100.0
    );
    CREATE INDEX IF NOT EXISTS idx_grid_cells_geom ON grid_cells USING GIST (geom);
    CREATE INDEX IF NOT EXISTS idx_grid_cells_centroid ON grid_cells USING GIST (centroid);
    CREATE INDEX IF NOT EXISTS idx_grid_cells_region ON grid_cells (region_id);
    """)

    # 5. weather_obs table
    op.execute("""
    CREATE TABLE IF NOT EXISTS weather_obs (
        id VARCHAR(36) PRIMARY KEY,
        cell_id VARCHAR(36) REFERENCES grid_cells(id) ON DELETE CASCADE,
        location_id VARCHAR(36) REFERENCES locations(id) ON DELETE CASCADE,
        ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        precip_mm DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        temp_c DOUBLE PRECISION NOT NULL DEFAULT 20.0,
        humidity DOUBLE PRECISION NOT NULL DEFAULT 70.0,
        soil_moisture DOUBLE PRECISION NOT NULL DEFAULT 0.28,
        pressure DOUBLE PRECISION NOT NULL DEFAULT 1013.25,
        wind DOUBLE PRECISION NOT NULL DEFAULT 5.0,
        source VARCHAR(60) NOT NULL DEFAULT 'open_meteo',
        CONSTRAINT uq_weather_obs_cell_ts_source UNIQUE (cell_id, ts, source)
    );
    CREATE INDEX IF NOT EXISTS idx_weather_obs_ts ON weather_obs (ts);
    CREATE INDEX IF NOT EXISTS idx_weather_obs_cell ON weather_obs (cell_id);
    CREATE INDEX IF NOT EXISTS idx_weather_obs_loc ON weather_obs (location_id);
    """)

    # 6. river_obs table
    op.execute("""
    CREATE TABLE IF NOT EXISTS river_obs (
        id VARCHAR(36) PRIMARY KEY,
        station_or_cell_id VARCHAR(60) NOT NULL,
        ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        discharge_m3s DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        level_m DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        source VARCHAR(30) NOT NULL DEFAULT 'sensor'
    );
    CREATE INDEX IF NOT EXISTS idx_river_obs_station_ts ON river_obs (station_or_cell_id, ts);
    """)

    # 7. predictions table
    op.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id VARCHAR(36) PRIMARY KEY,
        cell_id VARCHAR(36) REFERENCES grid_cells(id) ON DELETE CASCADE,
        location_id VARCHAR(36) REFERENCES locations(id) ON DELETE CASCADE,
        issued_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        horizon_h INTEGER NOT NULL DEFAULT 1,
        prob DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        severity VARCHAR(30) NOT NULL DEFAULT 'low',
        drivers JSONB NOT NULL DEFAULT '{}'::jsonb,
        model_version VARCHAR(60) NOT NULL DEFAULT 'lightgbm-v1.0'
    );
    CREATE INDEX IF NOT EXISTS idx_predictions_issued ON predictions (issued_at);
    CREATE INDEX IF NOT EXISTS idx_predictions_cell_horizon ON predictions (cell_id, horizon_h);
    """)

    # 8. users table
    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        email VARCHAR(160) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(40) NOT NULL DEFAULT 'citizen',
        name VARCHAR(120) NOT NULL,
        org VARCHAR(160),
        region_id VARCHAR(36) REFERENCES regions(id),
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
    );
    CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
    CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
    """)

    # 9. subscriptions table
    op.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        channel VARCHAR(30) NOT NULL,
        target VARCHAR(255) NOT NULL,
        locations JSONB NOT NULL DEFAULT '{}'::jsonb,
        min_severity VARCHAR(30) NOT NULL DEFAULT 'high',
        language VARCHAR(10) NOT NULL DEFAULT 'en',
        verified_at TIMESTAMP WITHOUT TIME ZONE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
    );
    CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions (user_id);
    """)

    # 10. alerts table
    op.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id VARCHAR(36) PRIMARY KEY,
        region_id VARCHAR(36) NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
        cell_id VARCHAR(36) REFERENCES grid_cells(id) ON DELETE SET NULL,
        location_id VARCHAR(36) REFERENCES locations(id) ON DELETE SET NULL,
        severity VARCHAR(30) NOT NULL,
        message_i18n JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
        expires_at TIMESTAMP WITHOUT TIME ZONE,
        status VARCHAR(30) NOT NULL DEFAULT 'active',
        issued_by VARCHAR(120) NOT NULL DEFAULT 'system',
        title VARCHAR(150),
        message TEXT,
        risk_score DOUBLE PRECISION DEFAULT 0.5
    );
    CREATE INDEX IF NOT EXISTS idx_alerts_region ON alerts (region_id);
    CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status);
    CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts (created_at);
    """)

    # 11. alert_deliveries table
    op.execute("""
    CREATE TABLE IF NOT EXISTS alert_deliveries (
        id VARCHAR(36) PRIMARY KEY,
        alert_id VARCHAR(36) NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
        subscription_id VARCHAR(36) REFERENCES subscriptions(id) ON DELETE SET NULL,
        channel VARCHAR(30) NOT NULL,
        status VARCHAR(40) NOT NULL,
        provider_msg_id VARCHAR(120),
        error TEXT,
        ts TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
    );
    CREATE INDEX IF NOT EXISTS idx_alert_deliveries_alert ON alert_deliveries (alert_id);
    """)

    # 12. sensor_devices table
    op.execute("""
    CREATE TABLE IF NOT EXISTS sensor_devices (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(120) NOT NULL,
        geom GEOMETRY(Point, 4326) NOT NULL,
        api_key_hash VARCHAR(128) NOT NULL,
        last_seen TIMESTAMP WITHOUT TIME ZONE,
        river_name VARCHAR(80),
        warning_level_m DOUBLE PRECISION DEFAULT 3.5,
        danger_level_m DOUBLE PRECISION DEFAULT 5.0,
        is_simulated BOOLEAN DEFAULT FALSE,
        region_id VARCHAR(36) REFERENCES regions(id),
        status VARCHAR(20) DEFAULT 'online'
    );
    CREATE INDEX IF NOT EXISTS idx_sensor_devices_geom ON sensor_devices USING GIST (geom);
    """)


def downgrade() -> None:
    op.drop_table('sensor_devices')
    op.drop_table('alert_deliveries')
    op.drop_table('alerts')
    op.drop_table('subscriptions')
    op.drop_table('users')
    op.drop_table('predictions')
    op.drop_table('river_obs')
    op.drop_table('weather_obs')
    op.drop_table('grid_cells')
    op.drop_table('locations')
    op.drop_table('regions')

