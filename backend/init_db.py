"""初始化 SQLite 数据库：从 public/data_json/*.json 建表并导入数据。

用法：
    python -m backend.init_db
或：
    python backend/init_db.py
"""
import json
import os
import sqlite3

from backend.database import DB_PATH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "public", "data_json")


SCHEMA = """
DROP TABLE IF EXISTS charging_records;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS charger_specs;
DROP TABLE IF EXISTS operators;
DROP TABLE IF EXISTS cities;

CREATE TABLE cities (
    city_id      INTEGER PRIMARY KEY,
    city_name    TEXT,
    longitude    REAL,
    latitude     REAL,
    area_code    TEXT,
    population   INTEGER,
    gdp_billion  REAL
);

CREATE TABLE operators (
    operator_id   INTEGER PRIMARY KEY,
    operator_name TEXT,
    company_type  TEXT,
    founded_year  INTEGER,
    headquarters  TEXT
);

CREATE TABLE charger_specs (
    spec_id          INTEGER PRIMARY KEY,
    type_name        TEXT,
    power_kw         REAL,
    voltage_v        REAL,
    current_a        REAL,
    connector_type   TEXT,
    charge_time_min  INTEGER,
    cost_per_kwh     REAL
);

CREATE TABLE stations (
    station_id     INTEGER PRIMARY KEY,
    station_name    TEXT,
    address        TEXT,
    phone          TEXT,
    longitude      REAL,
    latitude       REAL,
    city_id        INTEGER,
    operator_id    INTEGER,
    spec_id        INTEGER,
    opening_hours  TEXT,
    has_restroom   INTEGER,
    parking_spots  INTEGER
);

CREATE TABLE users (
    user_id            TEXT PRIMARY KEY,
    username           TEXT,
    phone              TEXT,
    user_type          TEXT,
    vehicle_type       TEXT,
    vehicle_model      TEXT,
    registration_date  TEXT,
    total_charge_count INTEGER,
    total_charge_kwh   REAL,
    preferred_city_id  INTEGER
);

CREATE TABLE charging_records (
    record_id          TEXT PRIMARY KEY,
    user_id            TEXT,
    station_id          INTEGER,
    charge_start_time   TEXT,
    charge_end_time     TEXT,
    duration_minutes   INTEGER,
    energy_kwh         REAL,
    cost_yuan          REAL,
    payment_method     TEXT,
    start_soc          INTEGER,
    end_soc            INTEGER
);
"""


def load_json(name: str):
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def to_int(v):
    if v is None or v == "":
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def to_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def to_bool(v):
    if v is None:
        return None
    return 1 if str(v).strip().upper() in ("TRUE", "1", "YES") else 0


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # cities
    cities = load_json("expanded_cities.json")
    conn.executemany(
        "INSERT INTO cities VALUES (?,?,?,?,?,?,?)",
        [
            (
                to_int(r["city_id"]), r["city_name"],
                to_float(r["longitude"]), to_float(r["latitude"]),
                r["area_code"], to_int(r["population"]), to_float(r["gdp_billion"]),
            )
            for r in cities
        ],
    )

    # operators
    operators = load_json("operators_info.json")
    conn.executemany(
        "INSERT INTO operators VALUES (?,?,?,?,?)",
        [
            (
                to_int(r["operator_id"]), r["operator_name"],
                r["company_type"], to_int(r["founded_year"]), r["headquarters"],
            )
            for r in operators
        ],
    )

    # charger specs
    specs = load_json("charger_specifications.json")
    conn.executemany(
        "INSERT INTO charger_specs VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                to_int(r["spec_id"]), r["type_name"],
                to_float(r["power_kw"]), to_float(r["voltage_v"]),
                to_float(r["current_a"]), r["connector_type"],
                to_int(r["charge_time_min"]), to_float(r["cost_per_kwh"]),
            )
            for r in specs
        ],
    )

    # stations
    stations = load_json("expanded_stations.json")
    conn.executemany(
        "INSERT INTO stations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                to_int(r["station_id"]), r["station_name"],
                r["address"], r["phone"],
                to_float(r["longitude"]), to_float(r["latitude"]),
                to_int(r["city_id"]), to_int(r["operator_id"]), to_int(r["spec_id"]),
                r["opening_hours"], to_bool(r["has_restroom"]), to_int(r["parking_spots"]),
            )
            for r in stations
        ],
    )

    # users
    users = load_json("users.json")
    conn.executemany(
        "INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["user_id"], r["username"], r["phone"],
                r["user_type"], r["vehicle_type"], r["vehicle_model"],
                r["registration_date"], to_int(r["total_charge_count"]),
                to_float(r["total_charge_kwh"]), to_int(r["preferred_city_id"]),
            )
            for r in users
        ],
    )

    # charging records
    records = load_json("charging_records.json")
    conn.executemany(
        "INSERT INTO charging_records VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["record_id"], r["user_id"], to_int(r["station_id"]),
                r["charge_start_time"], r["charge_end_time"],
                to_int(r["duration_minutes"]), to_float(r["energy_kwh"]),
                to_float(r["cost_yuan"]), r["payment_method"],
                to_int(r["start_soc"]), to_int(r["end_soc"]),
            )
            for r in records
        ],
    )

    conn.commit()

    # 打印计数
    for table in ["cities", "operators", "charger_specs", "stations", "users", "charging_records"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n} rows")

    conn.close()
    print(f"数据库已生成: {DB_PATH}")


if __name__ == "__main__":
    main()
