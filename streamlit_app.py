import json
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


def time_to_seconds(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    parts = text.split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        return None
    try:
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    except ValueError:
        return None


def seconds_to_hms(seconds):
    if seconds is None or pd.isna(seconds):
        return "N/D"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_distance_km(value):
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    match = re.search(r"(\d+[\.,]?\d*)", text)
    if not match:
        return None
    number = match.group(1).replace(",", ".")
    try:
        numeric = float(number)
    except ValueError:
        return None
    if "KM" in text:
        return numeric
    if "M" in text:
        return numeric / 1000
    return None


def pace_seconds_to_str(seconds_per_km):
    if seconds_per_km is None or pd.isna(seconds_per_km):
        return "N/D"
    total = int(seconds_per_km)
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02d}:{secs:02d} /km"


def map_age_group(code):
    if not code or code == "SIN_CATEGORIA":
        return "SIN_CATEGORIA"
    code = str(code).upper()
    if code.startswith("JV1"):
        return "Joven 11-15"
    if code.startswith("JV2"):
        return "Joven 16-19"
    if code.startswith("SN"):
        return "Senior 20-34"
    if code.startswith("VTA"):
        return "Veteranos A 35-44"
    if code.startswith("VTB"):
        return "Veteranos B 45-54"
    if code.startswith("VTC"):
        return "Veteranos C 55-64"
    if code.startswith("VTD"):
        return "Veteranos D 65+"
    return "OTRA"


def normalize_category_base(value):
    if value is None:
        return ""
    text = str(value).strip().upper()
    if not text:
        return ""
    text = re.sub(r"[-\s]*\d+$", "", text)
    text = re.sub(r"[MF]$", "", text)
    return text


def detect_gender(sexo_value, category_value):
    for candidate in (sexo_value, category_value):
        if candidate is None:
            continue
        text = str(candidate).strip().upper()
        match = re.search(r"\b([MF])\b", text)
        if match:
            return match.group(1)
        if text.startswith("M"):
            return "M"
        if text.startswith("F"):
            return "F"
    return None


@st.cache_data
def load_data():
    candidate_paths = [
        Path("data/salidas.json"),
        Path("..") / "data" / "salidas.json",
        Path("../data/salidas.json"),
    ]
    data_path = next((p for p in candidate_paths if p.exists()), None)
    if data_path is None:
        raise FileNotFoundError("No se encontro data/salidas.json. Ejecuta el exportador primero.")

    with data_path.open("r", encoding="utf-8") as file_handle:
        records = json.load(file_handle)

    df = pd.DataFrame(records)
    if "categoria" not in df.columns and "categoría" in df.columns:
        df["categoria"] = df["categoría"]

    for col in ["tiempo", "sexo", "carrera", "distancia", "nombre", "apellido"]:
        if col not in df.columns:
            df[col] = None

    df["year"] = pd.to_numeric(df["carrera"], errors="coerce")
    df["time_seconds"] = df["tiempo"].apply(time_to_seconds)
    df["categoria"] = df.get("categoria", pd.Series(dtype=str)).fillna("SIN_CATEGORIA")
    df["category_raw"] = df["categoria"].astype(str).str.strip()
    df["category_base"] = df["category_raw"].apply(normalize_category_base)
    df["gender"] = [
        detect_gender(sexo, cat)
        for sexo, cat in zip(df["sexo"].tolist(), df["category_raw"].tolist())
    ]
    df["age_group"] = df["category_base"].apply(map_age_group)
    df["distance_km"] = df["distancia"].apply(parse_distance_km)
    df["pace_seconds"] = df["time_seconds"] / df["distance_km"]
    df["runner_name"] = (df["nombre"].fillna("") + " " + df["apellido"].fillna("")).str.strip()

    return df


st.set_page_config(page_title="Race Analysis Dashboard", layout="wide")
st.title("Race Analysis Dashboard")

if st.sidebar.button("Recargar datos"):
    st.cache_data.clear()
    st.rerun()

try:
    df = load_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()


race_tab, runner_tab = st.tabs(["Race Analysis", "Runner Analysis"])

with race_tab:
    st.subheader("Race Analysis View")

    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    year = st.selectbox("Selecciona una carrera (ano)", years)

    df_year = df[df["year"] == year].copy()

    gender_options = ["Todos"] + sorted(df_year["gender"].dropna().unique().tolist())
    gender_choice = st.selectbox("Genero", gender_options)

    age_options = [
        "Todos"
    ] + sorted(
        df_year["age_group"]
        .dropna()
        .loc[lambda s: ~s.isin(["OTRA", "SIN_CATEGORIA"])]
        .unique()
        .tolist()
    )
    age_choice = st.selectbox("Grupo de edad", age_options)


    if gender_choice != "Todos":
        df_year = df_year[df_year["gender"] == gender_choice]
    if age_choice != "Todos":
        df_year = df_year[df_year["age_group"] == age_choice]

    df_times = df_year.dropna(subset=["time_seconds"])

    if df_times.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        min_time = seconds_to_hms(df_times["time_seconds"].min())
        max_time = seconds_to_hms(df_times["time_seconds"].max())
        mean_time = seconds_to_hms(df_times["time_seconds"].mean())
        median_time = seconds_to_hms(df_times["time_seconds"].median())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Min", min_time)
        col2.metric("Max", max_time)
        col3.metric("Media", mean_time)
        col4.metric("Mediana", median_time)

        df_times = df_times.assign(time_minutes=df_times["time_seconds"] / 60)
        fig = px.histogram(
            df_times,
            x="time_minutes",
            nbins=40,
            title="Distribucion de tiempos (minutos)",
            labels={"time_minutes": "Minutos"},
        )
        st.plotly_chart(fig, use_container_width=True)


with runner_tab:
    st.subheader("Runner Analysis View")

    runners = sorted(df["runner_name"].dropna().unique().tolist())
    runner = st.selectbox("Selecciona un corredor", runners)

    runner_df = df[df["runner_name"] == runner].copy()
    runner_df = runner_df.dropna(subset=["year"]).sort_values("year")

    if runner_df.empty:
        st.warning("No hay datos para el corredor seleccionado.")
    else:
        runner_df["finish_time"] = runner_df["time_seconds"].apply(seconds_to_hms)
        runner_df["pace"] = runner_df["pace_seconds"].apply(pace_seconds_to_str)

        table = runner_df[["year", "finish_time", "pace", "puesto"]].rename(
            columns={"year": "Ano", "finish_time": "Tiempo", "puesto": "Puesto"}
        )
        st.dataframe(table, use_container_width=True)

        race_years = runner_df["year"].dropna().astype(int).tolist()
        race_year = st.selectbox("Ver detalles de la carrera", race_years)

        race_df = df[df["year"] == race_year].dropna(subset=["time_seconds"]).copy()
        runner_race = runner_df[runner_df["year"] == race_year].dropna(subset=["time_seconds"]).head(1)

        if runner_race.empty:
            st.warning("No hay tiempo registrado para este corredor en esa carrera.")
        else:
            runner_time = runner_race.iloc[0]["time_seconds"]
            fig = px.histogram(
                race_df.assign(time_minutes=race_df["time_seconds"] / 60),
                x="time_minutes",
                nbins=40,
                title=f"Distribucion de tiempos en {race_year}",
                labels={"time_minutes": "Minutos"},
            )
            fig.add_vline(x=runner_time / 60, line_color="red", line_width=2)
            st.plotly_chart(fig, use_container_width=True)

            st.caption("La linea roja indica el tiempo del corredor en esa carrera.")
