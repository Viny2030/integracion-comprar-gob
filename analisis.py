import pandas as pd
import os
import unicodedata
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN E INFRAESTRUCTURA
# ==========================================
DATA_DIR = "/app/data" if os.path.exists("/app") else os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ==========================================
# 2. MATRIZ TEÓRICA (Refinada con casos reales)
# ==========================================
MATRIZ_TEORICA = {
    "Privatización / Concesión": {
        "keywords": [
            "concesion",
            "privatizacion",
            "venta de pliegos",
            "adjudicacion",
            "subvaluacion",
        ],
        "transferencia": "Estado a Privados",
        "mecanismo": "Transferencia por enajenación de activos públicos o gestión de servicios estratégicos.",
        "peso": 9.0,
    },
    "Contratos Públicos": {
        "keywords": [
            "obra publica",
            "licitacion",
            "contratacion directa",
            "sobreprecio",
            "subfusiles",
            "mantenimiento",
            "reparacion",
        ],
        "transferencia": "Estado a Empresas Contratistas",
        "mecanismo": "Sobreprecios, direccionamiento o falta de competencia en la provisión de bienes.",
        "peso": 8.5,
    },
    "Tarifas Servicios Públicos": {
        "keywords": [
            "cuadro tarifario",
            "aumento de tarifa",
            "revision tarifaria",
            "ente regulador",
            "peaje",
            "canon",
        ],
        "transferencia": "Usuarios a Concesionarias",
        "mecanismo": "Aumentos discrecionales que impactan en la rentabilidad extraordinaria de empresas.",
        "peso": 7.5,
    },
    "Precios de Consumo Regulados": {
        "keywords": [
            "precios justos",
            "abastecimiento",
            "consumo masivo",
            "canasta basica",
            "viveres",
            "alimento",
            "forraje",
        ],
        "transferencia": "Consumidores a Productores",
        "mecanismo": "Regulación de precios que favorece la concentración económica y castiga al consumidor.",
        "peso": 6.5,
    },
    "Salarios y Paritarias": {
        "keywords": [
            "paritaria",
            "salario minimo",
            "convenio colectivo",
            "ajuste salarial",
            "indice inflacionario",
        ],
        "transferencia": "Asalariados a Empleadores/Estado",
        "mecanismo": "Pérdida del poder adquisitivo mediante ajustes por debajo de la inflación real.",
        "peso": 5.5,
    },
    "Jubilaciones / Pensiones": {
        "keywords": [
            "movilidad jubilatoria",
            "haber minimo",
            "anses",
            "pensionados",
            "ajuste previsional",
        ],
        "transferencia": "Jubilados al Estado",
        "mecanismo": "Reducción del gasto público mediante la erosión del ingreso de los pasivos.",
        "peso": 10.0,
    },
    "Traslado de Impuestos": {
        "keywords": [
            "iva",
            "ingresos brutos",
            "retenciones",
            "doble imposicion",
            "presion tributaria",
        ],
        "transferencia": "Contribuyentes al Estado",
        "mecanismo": "Carga impositiva regresiva que afecta proporcionalmente más a los sectores bajos.",
        "peso": 9.5,
    },
}


def limpiar_texto_curado(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def analizar_boletin(df):
    if df.empty:
        return df, None, pd.DataFrame()

    df["texto_clean"] = df["detalle"].apply(limpiar_texto_curado)
    df["tipo_decision"] = "No identificado"
    df["transferencia"] = "No identificado"
    df["indice_total"] = 0.0  # Flotante para evitar error de Dtype

    for categoria, info in MATRIZ_TEORICA.items():
        mask = df["texto_clean"].str.contains("|".join(info["keywords"]), na=False)
        df.loc[mask, "tipo_decision"] = categoria
        df.loc[mask, "transferencia"] = info["transferencia"]
        # Incremento si es Contratación Directa
        factor = (
            1.2
            if "tipo_proceso" in df.columns and "Directa" in str(df["tipo_proceso"])
            else 1.0
        )
        df.loc[mask, "indice_total"] = info["peso"] * factor

    df["indice_fenomeno_corruptivo"] = df["indice_total"].clip(0, 10).round(1)

    def evaluar_riesgo(score):
        if score >= 8:
            return "Alto"
        if score >= 5:
            return "Medio"
        return "Bajo"

    df["nivel_riesgo_teorico"] = df["indice_fenomeno_corruptivo"].apply(evaluar_riesgo)

    fecha_str = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(DATA_DIR, f"reporte_fenomenos_{fecha_str}.xlsx")

    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Analisis")
            # HOJA DE GLOSARIO PARA EL MONITOR
            glosario_df = pd.DataFrame(
                [
                    {
                        "Variable": "tipo_decision",
                        "Definición": "Escenario detectado de la Gran Corrupción.",
                    },
                    {
                        "Variable": "transferencia",
                        "Definición": "Sector económico afectado por la medida.",
                    },
                    {
                        "Variable": "indice_fenomeno_corruptivo",
                        "Definición": "Intensidad del fenómeno (0-10).",
                    },
                ]
            )
            glosario_df.to_excel(writer, index=False, sheet_name="Glosario")
        return df, output_path, pd.DataFrame()
    except Exception as e:
        print(f"Error: {e}")
        return df, None, pd.DataFrame()