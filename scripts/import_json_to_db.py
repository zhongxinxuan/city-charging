import json
from pathlib import Path

import psycopg


BASE_DIR = Path(__file__).resolve().parent.parent
JSON_DIR = BASE_DIR / "public" / "data_json"

DB_CONFIG = {
    "dbname": "car_charging_db",
    "user": "postgres",
    "password": "274531",
    "host": "localhost",
    "port": 5432,
}

IMPORT_TASKS = [
    {
        "filename": "expanded_cities.json",
        "table": "charging_system.cities",
        "fields": [
            "city_id",
            "city_name",
            "longitude",
            "latitude",
            "area_code",
            "population",
            "gdp_billion",
        ],
        "conflict": "city_id",
    },
    {
        "filename": "operators_info.json",
        "table": "charging_system.operators",
        "fields": [
            "operator_id",
            "operator_name",
            "company_type",
            "founded_year",
            "headquarters",
        ],
        "conflict": "operator_id",
    },
    {
        "filename": "charger_specifications.json",
        "table": "charging_system.charger_specs",
        "fields": [
            "spec_id",
            "type_name",
            "power_kw",
            "voltage_v",
            "current_a",
            "connector_type",
            "charge_time_min",
            "cost_per_kwh",
        ],
        "conflict": "spec_id",
    },
    {
        "filename": "expanded_stations.json",
        "table": "charging_system.stations",
        "fields": [
            "station_id",
            "station_name",
            "address",
            "phone",fa
            "longitude",
            "latitude",
            "city_id",
            "operator_id",
            "spec_id",
            "opening_hours",
            "has_restroom",
            "parking_spots",
        ],
        "conflict": "station_id",
    },
    {
        "filename": "users.json",
        "table": "charging_system.users",
        "fields": [
            "user_id",
            "username",
            "phone",
            "user_type",
            "vehicle_type",
            "vehicle_model",
            "registration_date",
            "total_charge_count",
            "total_charge_kwh",
            "preferred_city_id",
        ],
        "conflict": "user_id",
    },
    {
        "filename": "charging_records.json",
        "table": "charging_system.charging_records",
        "fields": [
            "record_id",
            "user_id",
            "station_id",
            "charge_start_time",
            "charge_end_time",
            "duration_minutes",
            "energy_kwh",
            "cost_yuan",
            "payment_method",
            "start_soc",
            "end_soc",
        ],
        "conflict": "record_id",
    },
]


def normalize_value(value):
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    return value


def load_json(filename: str) -> list[dict]:
    json_path = JSON_DIR / filename

    with json_path.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)


def build_insert_sql(table: str, fields: list[str], conflict: str) -> str:
    columns = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))

    return f"""
    INSERT INTO {table} ({columns})
    VALUES ({placeholders})
    ON CONFLICT ({conflict}) DO NOTHING;
    """


def test_connection() -> None:
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database();")
            result = cur.fetchone()
            print("Database connection:", result[0])


def import_table(task: dict) -> None:
    rows = load_json(task["filename"])
    sql = build_insert_sql(task["table"], task["fields"], task["conflict"])

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            for row in rows:
                values = tuple(normalize_value(row[field]) for field in task["fields"])
                cur.execute(sql, values)

        conn.commit()

    print(f"Imported {task['table']}: {len(rows)} rows")


def import_all() -> None:
    for task in IMPORT_TASKS:
        import_table(task)


if __name__ == "__main__":
    test_connection()
    import_all()
