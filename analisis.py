import pandas as pd
import os
import unicodedata
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN E INFRAESTRUCTURA
# ==========================================
if os.path.exists("/app"):
    DATA_DIR = "/app/data"
else:
    DATA_DIR = os.path.join(os.getcwd(), "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ==========================================
# 2. MATRIZ TEÓRICA (Basada en "Great Corruption")
# ==========================================
# Mapeo de los 7 escenarios y sectores afectados (Transferencia)
MATRIZ_TEORICA = {
    "Privatización / Concesión": {
        "keywords": [
            "concesión",
            "privatización",
            "venta de pliegos",
            "adjudicación",
            "licitación pública",
            "subvaluación",
        ],
        "transferencia": "Estado a Privados",
        "peso": 9,
    },
    "Contratos Públicos": {
        "keywords": [
            "obra pública",
            "redeterminación de precios",
            "contratación directa",
            "ajuste de contrato",
            "sobreprecio",
        ],
        "transferencia": "Estado a Empresas Contratistas",
        "peso": 8,
    },
    "Tarifas Servicios Públicos": {
        "keywords": [
            "cuadro tarifario",
            "aumento de tarifa",
            "revisión tarifaria",
            "ente regulador",
            "peaje",
            "canon",
        ],
        "transferencia": "Usuarios a Concesionarias",
        "peso": 7,
    },
    "Precios de Consumo Regulados": {
        "keywords": [
            "precios justos",
            "abastecimiento",
            "consumo masivo",
            "canasta básica",
            "regulación de precios",
        ],
        "transferencia": "Consumidores a Productores",
        "peso": 6,
    },
    "Salarios y Paritarias": {
        "keywords": [
            "paritaria",
            "salario mínimo",
            "convenio colectivo",
            "ajuste salarial",
            "índice inflacionario",
        ],
        "transferencia": "Asalariados a Empleadores/Estado",
        "peso": 5,
    },
    "Jubilaciones / Pensiones": {
        "keywords": [
            "movilidad jubilatoria",
            "haber mínimo",
            "anses",
            "pensionados",
            "ajuste previsional",
        ],
        "transferencia": "Jubilados al Estado",
        "peso": 10,
    },
    "Traslado de Impuestos": {
        "keywords": [
            "iva",
            "ingresos brutos",
            "retenciones",
            "doble imposición",
            "presión tributaria",
        ],
        "transferencia": "Contribuyentes al Estado",
        "peso": 9,
    },
}


def limpiar_texto_curado(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


# ==========================================
# 3. MOTOR DE CÁLCULO Y CLASIFICACIÓN
# ==========================================
def analizar_boletin(df):
    if df.empty:
        return df, None, pd.DataFrame()

    df["texto_clean"] = df["detalle"].apply(limpiar_texto_curado)

    # Inicialización de columnas requeridas
    df["tipo_decision"] = "No identificado"
    df["transferencia"] = "No identificado"
    df["indice_total"] = 0

    for categoria, info in MATRIZ_TEORICA.items():
        mask = df["texto_clean"].str.contains("|".join(info["keywords"]), na=False)
        df.loc[mask, "tipo_decision"] = categoria
        df.loc[mask, "transferencia"] = info["transferencia"]
        df.loc[mask, "indice_total"] = (
            info["peso"] * 1.1
        )  # Factor de discrecionalidad base

    # 4. Ajuste de Escala (0 a 10) según pedido
    # El peso máximo teórico es 10, ajustamos para que no exceda el límite.
    df["indice_fenomeno_corruptivo"] = df["indice_total"].clip(0, 10).round(1)

    # 5. Evaluación Cualitativa del Riesgo
    def evaluar_riesgo(score):
        if score >= 8:
            return "Alto"
        if score >= 5:
            return "Medio"
        return "Bajo"

    df["nivel_riesgo_teorico"] = df["indice_fenomeno_corruptivo"].apply(evaluar_riesgo)

    # 6. Preparación de Salida Final (Columnas Solicitadas)
    cols_finales = [
        "fecha",
        "tipo_decision",
        "transferencia",
        "indice_fenomeno_corruptivo",
        "nivel_riesgo_teorico",
        "link",
    ]

    fecha_str = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(DATA_DIR, f"reporte_fenomenos_{fecha_str}.xlsx")

    try:
        # Exportamos solo las columnas de interés académico
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df[cols_finales].to_excel(writer, index=False, sheet_name="Analisis")
        return df, output_path, pd.DataFrame()
    except Exception as e:
        print(f"Error al exportar: {e}")
        return df, None, pd.DataFrame()


if __name__ == "__main__":
    # Prueba rápida local
    data_test = {
        "fecha": [datetime.now().strftime("%Y-%m-%d")],
        "detalle": ["Ajuste en la movilidad jubilatoria y pensiones por decreto."],
        "link": ["https://boletinoficial.gob.ar/norma/1"],
    }
    test_df = pd.DataFrame(data_test)
    res, path, _ = analizar_boletin(test_df)
    print(f"Análisis completado. Archivo generado en: {path}")