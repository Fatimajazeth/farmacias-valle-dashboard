from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Farmacias Valle",
    page_icon="💊",
    layout="wide"
)

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv(Path(__file__).parent / "datos.csv")
    df["mes"] = pd.to_datetime(df["mes"])
    return df

df = cargar_datos()

# Paleta de colores
colores = [
    "#00695C", "#26A69A", "#1565C0",
    "#80CBC4", "#90CAF9"
]

# Encabezado
st.title("💊 Farmacias Valle")
st.subheader(
    "Desempeño comercial y oportunidades de abastecimiento"
)

st.write(
    "Tablero de inteligencia de negocios para apoyar "
    "las decisiones de ventas, compras e inventarios."
)

# Filtros interactivos
st.sidebar.header("Filtros interactivos")

anio = st.sidebar.selectbox(
    "Selecciona el año",
    sorted(df["anio"].unique(), reverse=True)
)

categorias = st.sidebar.multiselect(
    "Selecciona las categorías",
    sorted(df["categoria"].unique()),
    default=sorted(df["categoria"].unique())
)

# Filtrar periodo actual y anterior
actual = df[
    (df["anio"] == anio) &
    (df["categoria"].isin(categorias))
]

anterior = df[
    (df["anio"] == anio - 1) &
    (df["categoria"].isin(categorias))
]

if actual.empty:
    st.warning("Selecciona al menos una categoría con datos.")
    st.stop()

# Funciones para calcular indicadores
def division(a, b):
    return a / b if b != 0 else 0

def variacion(a, b):
    if b == 0:
        return None
    return f"{(a-b)/b*100:+.2f}%"

# Calcular KPIs
ingresos = actual["ingreso_mensual"].sum()
ingresos_ant = anterior["ingreso_mensual"].sum()

unidades = actual["unidades_vendidas"].sum()
unidades_ant = anterior["unidades_vendidas"].sum()

precio = division(ingresos, unidades)
precio_ant = division(ingresos_ant, unidades_ant)

# Tarjetas de indicadores
st.header("Indicadores clave de desempeño")

st.caption(f"Periodo seleccionado: {anio} vs. {anio-1}")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Ingresos totales",
    f"${ingresos:,.2f}",
    variacion(ingresos, ingresos_ant)
)

c2.metric(
    "Unidades vendidas",
    f"{unidades:,.0f}",
    variacion(unidades, unidades_ant)
)

c3.metric(
    "Ingreso por unidad",
    f"${precio:,.2f}",
    variacion(precio, precio_ant)
)

if anterior.empty:
    st.caption("No existe un periodo anterior disponible.")

st.divider()

# Gráfica 1: Tendencia
mensual = actual.groupby("mes")[
    "ingreso_mensual"
].sum().reset_index()

fig1 = px.line(
    mensual,
    x="mes",
    y="ingreso_mensual",
    markers=True,
    title="Evolución mensual de ingresos",
    color_discrete_sequence=colores,
    labels={
        "mes": "Mes",
        "ingreso_mensual": "Ingresos ($)"
    }
)

fig1.update_layout(template="plotly_white")

# Gráfica 2: Comparación
categoria = actual.groupby("categoria")[
    "ingreso_mensual"
].sum().reset_index()

categoria = categoria.sort_values("ingreso_mensual")

fig2 = px.bar(
    categoria,
    x="ingreso_mensual",
    y="categoria",
    orientation="h",
    title="Ingresos por categoría",
    color="categoria",
    color_discrete_sequence=colores,
    labels={
        "categoria": "Categoría",
        "ingreso_mensual": "Ingresos ($)"
    }
)

fig2.update_layout(
    template="plotly_white",
    showlegend=False
)

# Gráfica 3: Distribución
fig3 = px.pie(
    categoria,
    names="categoria",
    values="ingreso_mensual",
    hole=0.5,
    title="Participación en los ingresos",
    color_discrete_sequence=colores
)

fig3.update_traces(
    textinfo="percent+label"
)

# Gráfica 4: Inventario y demanda
fig4 = px.scatter(
    actual,
    x="stock_disponible",
    y="unidades_vendidas",
    color="categoria",
    hover_name="producto_nombre",
    title="Inventario frente a unidades vendidas",
    color_discrete_sequence=colores,
    labels={
        "stock_disponible": "Stock disponible",
        "unidades_vendidas": "Unidades vendidas",
        "categoria": "Categoría"
    }
)

fig4.update_layout(template="plotly_white")

# Distribución de las gráficas
st.header("Análisis comercial")

izquierda, derecha = st.columns(2)

with izquierda:
    st.plotly_chart(fig1, use_container_width=True)

with derecha:
    st.plotly_chart(fig2, use_container_width=True)

izquierda2, derecha2 = st.columns(2)

with izquierda2:
    st.plotly_chart(fig3, use_container_width=True)

with derecha2:
    st.plotly_chart(fig4, use_container_width=True)

# Storytelling dinámico
st.divider()
st.header("Hallazgos y recomendaciones")

lider = categoria.loc[
    categoria["ingreso_mensual"].idxmax()
]

participacion = division(
    lider["ingreso_mensual"], ingresos
) * 100

mejor_mes = mensual.loc[
    mensual["ingreso_mensual"].idxmax()
]

st.info(
    f"La categoría {lider['categoria']} lidera los ingresos "
    f"del periodo seleccionado, con una participación "
    f"del {participacion:.2f}%."
)

st.write(
    f"El mes con mayores ingresos fue "
    f"{mejor_mes['mes'].strftime('%m/%Y')}, "
    f"con ${mejor_mes['ingreso_mensual']:,.2f}."
)

st.success(
    "Recomendación: el área de compras debe revisar "
    "los niveles de inventario de las categorías con "
    "mayor demanda y planificar el abastecimiento."
)

# Tabla de datos
with st.expander("Consultar datos detallados"):
    st.dataframe(actual, use_container_width=True)

# Fuente de información
st.divider()

st.caption(
    "Fuente: Farmacias Valle Demanda 1200. "
    "Elaboración propia con Python, Pandas, Plotly y Streamlit."
)

st.caption(
    "Limitaciones: no se dispone de costos, márgenes "
    "ni registros confirmados de desabastecimiento. "
    "La moneda no está especificada en el dataset."
)

import streamlit.components.v1 as components

components.html("""
<button onclick="window.parent.print()"
style="
    background-color: #00695C;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;">
    Imprimir / Guardar PDF
</button>
""", height=70)

import streamlit.components.v1 as components

components.html("""
<button onclick="window.parent.print()"
style="
    background-color: #00695C;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;">
    Imprimir / Guardar PDF
</button>
""", height=70)
