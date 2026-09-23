"""城市充电桩信息查询系统 API（线上部署版）。

- 数据源：SQLite（由 backend/init_db.py 从 public/data_json 导入）
- 同时托管 dist/ 前端静态文件，实现单服务部署
"""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.database import get_connection

app = FastAPI(title="城市充电桩信息查询系统 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_float(value):
    return float(value) if value is not None else None


def build_where(conditions: list[str]) -> str:
    if not conditions:
        return ""
    return "WHERE " + " AND ".join(conditions)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "城市充电桩系统后端运行正常",
    }


@app.get("/api/cities")
def get_cities():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT city_id, city_name, longitude, latitude, area_code, population, gdp_billion
            FROM cities ORDER BY city_id;
            """
        ).fetchall()

    return {
        "data": [
            {
                "city_id": r[0],
                "city_name": r[1],
                "longitude": to_float(r[2]),
                "latitude": to_float(r[3]),
                "area_code": r[4],
                "population": r[5],
                "gdp_billion": to_float(r[6]),
            }
            for r in rows
        ]
    }


@app.get("/api/operators")
def get_operators():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT operator_id, operator_name, company_type, founded_year, headquarters
            FROM operators ORDER BY operator_id;
            """
        ).fetchall()

    return {
        "data": [
            {
                "operator_id": r[0],
                "operator_name": r[1],
                "company_type": r[2],
                "founded_year": r[3],
                "headquarters": r[4],
            }
            for r in rows
        ]
    }


@app.get("/api/charger-specs")
def get_charger_specs():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT spec_id, type_name, power_kw, voltage_v, current_a,
                   connector_type, charge_time_min, cost_per_kwh
            FROM charger_specs ORDER BY spec_id;
            """
        ).fetchall()

    return {
        "data": [
            {
                "spec_id": r[0],
                "type_name": r[1],
                "power_kw": to_float(r[2]),
                "voltage_v": to_float(r[3]),
                "current_a": to_float(r[4]),
                "connector_type": r[5],
                "charge_time_min": r[6],
                "cost_per_kwh": to_float(r[7]),
            }
            for r in rows
        ]
    }


@app.get("/api/stations")
def get_stations(
    city_id: int | None = None,
    operator_id: int | None = None,
    keyword: str | None = None,
):
    conditions = []
    params = []

    if city_id is not None:
        conditions.append("s.city_id = ?")
        params.append(city_id)

    if operator_id is not None:
        conditions.append("s.operator_id = ?")
        params.append(operator_id)

    if keyword:
        conditions.append("(s.station_name LIKE ? OR s.address LIKE ?)")
        like = f"%{keyword}%"
        params.extend([like, like])

    where_sql = build_where(conditions)

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT s.station_id, s.station_name, c.city_name,
                   o.operator_name, cs.type_name, cs.power_kw
            FROM stations AS s
            JOIN cities AS c ON s.city_id = c.city_id
            JOIN operators AS o ON s.operator_id = o.operator_id
            JOIN charger_specs AS cs ON s.spec_id = cs.spec_id
            {where_sql}
            ORDER BY s.station_id
            LIMIT 50;
            """,
            params,
        ).fetchall()

    return {
        "data": [
            {
                "station_id": r[0],
                "station_name": r[1],
                "city_name": r[2],
                "operator_name": r[3],
                "type_name": r[4],
                "power_kw": to_float(r[5]),
            }
            for r in rows
        ]
    }


@app.get("/api/stations/{station_id}")
def get_station_detail(station_id: int):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT s.station_id, s.station_name, s.address, s.phone,
                   s.longitude, s.latitude, c.city_name, o.operator_name,
                   cs.type_name, cs.power_kw, cs.voltage_v, cs.current_a,
                   cs.connector_type, cs.charge_time_min, cs.cost_per_kwh,
                   s.opening_hours, s.has_restroom, s.parking_spots
            FROM stations AS s
            JOIN cities AS c ON s.city_id = c.city_id
            JOIN operators AS o ON s.operator_id = o.operator_id
            JOIN charger_specs AS cs ON s.spec_id = cs.spec_id
            WHERE s.station_id = ?;
            """,
            (station_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="充电站不存在")

    return {
        "data": {
            "station_id": row[0],
            "station_name": row[1],
            "address": row[2],
            "phone": row[3],
            "longitude": to_float(row[4]),
            "latitude": to_float(row[5]),
            "city_name": row[6],
            "operator_name": row[7],
            "type_name": row[8],
            "power_kw": to_float(row[9]),
            "voltage_v": to_float(row[10]),
            "current_a": to_float(row[11]),
            "connector_type": row[12],
            "charge_time_min": row[13],
            "cost_per_kwh": to_float(row[14]),
            "opening_hours": row[15],
            "has_restroom": bool(row[16]) if row[16] is not None else None,
            "parking_spots": row[17],
        }
    }


@app.get("/api/records")
def get_records(
    city_id: int | None = None,
    payment_method: str | None = None,
    keyword: str | None = None,
):
    conditions = []
    params = []

    if city_id is not None:
        conditions.append("s.city_id = ?")
        params.append(city_id)

    if payment_method:
        conditions.append("r.payment_method = ?")
        params.append(payment_method)

    if keyword:
        conditions.append("(r.record_id LIKE ? OR u.username LIKE ? OR s.station_name LIKE ?)")
        like = f"%{keyword}%"
        params.extend([like, like, like])

    where_sql = build_where(conditions)

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT r.record_id, u.username, s.station_name, c.city_name,
                   r.charge_start_time, r.duration_minutes,
                   r.energy_kwh, r.cost_yuan, r.payment_method
            FROM charging_records AS r
            JOIN users AS u ON r.user_id = u.user_id
            JOIN stations AS s ON r.station_id = s.station_id
            JOIN cities AS c ON s.city_id = c.city_id
            {where_sql}
            ORDER BY r.charge_start_time DESC
            LIMIT 50;
            """,
            params,
        ).fetchall()

    return {
        "data": [
            {
                "record_id": r[0],
                "username": r[1],
                "station_name": r[2],
                "city_name": r[3],
                "charge_start_time": r[4],
                "duration_minutes": r[5],
                "energy_kwh": to_float(r[6]),
                "cost_yuan": to_float(r[7]),
                "payment_method": r[8],
            }
            for r in rows
        ]
    }


@app.get("/api/records/{record_id}")
def get_record_detail(record_id: str):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT r.record_id, r.user_id, u.username, u.phone,
                   u.user_type, u.vehicle_type, u.vehicle_model,
                   s.station_id, s.station_name, c.city_name,
                   r.charge_start_time, r.charge_end_time,
                   r.duration_minutes, r.energy_kwh, r.cost_yuan,
                   r.payment_method, r.start_soc, r.end_soc
            FROM charging_records AS r
            JOIN users AS u ON r.user_id = u.user_id
            JOIN stations AS s ON r.station_id = s.station_id
            JOIN cities AS c ON s.city_id = c.city_id
            WHERE r.record_id = ?;
            """,
            (record_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="充电记录不存在")

    return {
        "data": {
            "record_id": row[0],
            "user_id": row[1],
            "username": row[2],
            "phone": row[3],
            "user_type": row[4],
            "vehicle_type": row[5],
            "vehicle_model": row[6],
            "station_id": row[7],
            "station_name": row[8],
            "city_name": row[9],
            "charge_start_time": row[10],
            "charge_end_time": row[11],
            "duration_minutes": row[12],
            "energy_kwh": to_float(row[13]),
            "cost_yuan": to_float(row[14]),
            "payment_method": row[15],
            "start_soc": row[16],
            "end_soc": row[17],
        }
    }


# ---------- 图表接口 ----------

@app.get("/api/charts/stations-by-city")
def get_stations_by_city_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.city_name, COUNT(s.station_id) AS station_count
            FROM cities AS c
            LEFT JOIN stations AS s ON c.city_id = s.city_id
            GROUP BY c.city_id, c.city_name
            ORDER BY station_count DESC, c.city_id;
            """
        ).fetchall()
    return {"data": [{"name": r[0], "value": r[1]} for r in rows]}


@app.get("/api/charts/operator-share")
def get_operator_share_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT o.operator_name, COUNT(s.station_id) AS station_count
            FROM operators AS o
            LEFT JOIN stations AS s ON o.operator_id = s.operator_id
            GROUP BY o.operator_id, o.operator_name
            ORDER BY station_count DESC, o.operator_id;
            """
        ).fetchall()
    return {"data": [{"name": r[0], "value": r[1]} for r in rows]}


@app.get("/api/charts/station-type-distribution")
def get_station_type_distribution_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT cs.type_name, COUNT(s.station_id) AS station_count
            FROM charger_specs AS cs
            LEFT JOIN stations AS s ON cs.spec_id = s.spec_id
            GROUP BY cs.type_name
            ORDER BY station_count DESC, cs.type_name;
            """
        ).fetchall()
    return {"data": [{"name": r[0], "value": r[1]} for r in rows]}


@app.get("/api/charts/payment-method-distribution")
def get_payment_method_distribution_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT r.payment_method, COUNT(r.record_id) AS record_count
            FROM charging_records AS r
            GROUP BY r.payment_method
            ORDER BY record_count DESC;
            """
        ).fetchall()
    return {
        "data": [
            {"name": r[0] if r[0] else "未知", "value": r[1]}
            for r in rows
        ]
    }


@app.get("/api/charts/records-by-city")
def get_records_by_city_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.city_name, COUNT(r.record_id) AS record_count
            FROM cities AS c
            LEFT JOIN stations AS s ON c.city_id = s.city_id
            LEFT JOIN charging_records AS r ON s.station_id = r.station_id
            GROUP BY c.city_id, c.city_name
            ORDER BY record_count DESC, c.city_id;
            """
        ).fetchall()
    return {"data": [{"name": r[0], "value": r[1]} for r in rows]}


@app.get("/api/charts/avg-cost-by-city")
def get_avg_cost_by_city_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.city_name, ROUND(AVG(r.cost_yuan), 2) AS avg_cost
            FROM cities AS c
            JOIN stations AS s ON c.city_id = s.city_id
            JOIN charging_records AS r ON s.station_id = r.station_id
            GROUP BY c.city_id, c.city_name
            ORDER BY avg_cost DESC;
            """
        ).fetchall()
    return {"data": [{"name": r[0], "value": to_float(r[1])} for r in rows]}


@app.get("/api/charts/avg-energy-by-city")
def get_avg_energy_by_city_chart():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.city_name, ROUND(AVG(r.energy_kwh), 2) AS avg_energy
            FROM cities AS c
            JOIN stations AS s ON c.city_id = s.city_id
            JOIN charging_records AS r ON s.station_id = r.station_id
            GROUP BY c.city_id, c.city_name
            ORDER BY avg_energy DESC;
            """
        ).fetchall()
    return {"data": [{"name": r[0], "value": to_float(r[1])} for r in rows]}


# ---------- 托管前端静态文件（SPA fallback） ----------

DIST_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist"
)


@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    if full_path:
        candidate = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
    index = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return {"message": "前端未构建，请先运行 npm run build"}
