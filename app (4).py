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
    "#15354E", "#F5A623", "#5484A3",
    "#9BB5C9", "#FFD080"
]


st.markdown("""
<style>

.stApp {
    background-color: #E9EDF2;
    color: #15354E;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 0.5rem;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background-color: #15354E;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h2 {
    color: white;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 3px 8px #00000015;
}

[data-testid="stMetricValue"] {
    color: #15354E;
    font-size: 26px;
}

[data-testid="stMetricLabel"] p {
    color: #15354E;
}

[data-testid="stPlotlyChart"] {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 3px 8px #00000015;
    padding: 4px;
}

h1 {
    font-size: 26px !important;
    color: #15354E;
}

h2 {
    font-size: 19px !important;
}

h3 {
    font-size: 16px !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

hr {
    margin: 5px 0 !important;
}

</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>

.block-container {
    padding: 0.8rem 1.5rem !important;
    max-width: 100% !important;
}

[data-testid="stSidebar"] {
    min-width: 210px !important;
    max-width: 210px !important;
}

[data-testid="stSidebarContent"] {
    padding-top: 0.5rem !important;
}

[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 10px !important;
}

[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
    flex: 1 1 0 !important;
}

[data-testid="stVerticalBlock"] {
    gap: 5px !important;
}

[data-testid="stMetric"] {
    padding: 8px !important;
}

[data-testid="stMetricValue"] {
    font-size: 24px !important;
}

h1 {
    font-size: 24px !important;
    padding: 0 !important;
    margin: 0 !important;
}

h2, h3 {
    font-size: 16px !important;
    padding: 0 !important;
}

p {
    font-size: 12px;
    margin-bottom: 3px !important;
}

[data-testid="stAlert"] {
    padding: 5px !important;
}

@page {
    size: A4 landscape;
    margin: 5mm;
}

@media print {

    header, footer,
    [data-testid="stToolbar"],
    [data-testid="stExpander"],
    [data-testid="stStatusWidget"],
    .modebar {
        display: none !important;
    }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }

    [data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0 !important;
        min-width: 0 !important;
    }

    [data-testid="stPlotlyChart"] {
        break-inside: avoid !important;
    }

    .block-container {
        padding: 5px !important;
    }

    body {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

}

</style>
""", unsafe_allow_html=True)

# Encabezado
st.title("💊 Farmacias Valle")
st.markdown(
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


for figura in [fig1, fig2, fig3, fig4]:
    figura.update_layout(
        height=210,
        margin=dict(l=15, r=15, t=40, b=15),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=11,
            color="#15354E"
        ),
        title_font_size=14,
        legend=dict(
            font=dict(size=9)
        )
    )


# Distribución de las gráficas


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

st.markdown("Hallazgos y recomendaciones")

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


st.caption(
    "Fuente: Farmacias Valle Demanda 1200. "
    "Elaboración propia con Python, Pandas, Plotly y Streamlit."
)

st.caption(
    "Limitaciones: no se dispone de costos, márgenes "
    "ni registros confirmados de desabastecimiento. "
    "La moneda no está especificada en el dataset."
)

