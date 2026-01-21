import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
# Busca automáticamente el archivo del día (o cambia el nombre si quieres analizar otro)
FECHA_HOY = datetime.now().strftime('%Y%m%d')
ARCHIVO_CSV = f"data/bora_{FECHA_HOY}.csv"  # Ruta donde lo guarda Docker
# Si lo corres en Windows directo sin Docker, la ruta sería:
# ARCHIVO_CSV = f"bora_{FECHA_HOY}.csv"

# --- CATEGORIZACIÓN TEÓRICA ---
# Diccionario para clasificar el tipo de fenómeno corruptivo
MECANISMOS_TEORIA = {
    'Tarifas/Precios': ['tarifas', 'cuadro tarifario', 'aumento', 'precio', 'ajuste'],
    'Privatizaciones/Concesiones': ['concesión', 'privatización', 'prórroga', 'licitación'],
    'Deuda/Fideicomisos': ['deuda', 'fideicomiso', 'letras', 'bonos', 'emisión'],
    'Subsidios/Exenciones': ['subsidio', 'exención', 'beneficio fiscal', 'condonación'],
    'Obra Pública': ['obra pública', 'redeterminación', 'contratación directa']
}

def clasificar_fenomeno(texto):
    """Etiqueta la norma según qué mecanismo de transferencia utiliza."""
    texto = str(texto).lower()
    etiquetas = []
    for categoria, palabras in MECANISMOS_TEORIA.items():
        if any(p in texto for p in palabras):
            etiquetas.append(categoria)

    return ", ".join(etiquetas) if etiquetas else "Otros/General"

def analizar_boletin():
    print(f"📂 Cargando archivo: {ARCHIVO_CSV}...")

    if not os.path.exists(ARCHIVO_CSV):
        print("❌ Error: No se encuentra el archivo CSV. Asegúrate de haber corrido el scraper primero.")
        return

    df = pd.read_csv(ARCHIVO_CSV)

    # 1. FILTRADO: Nos quedamos solo con las filas que dieron "Alerta: True"
    df_sospechosos = df[df['Alerta'] == True].copy()

    if df_sospechosos.empty:
        print("✅ Buenas noticias: No se detectaron fenómenos corruptivos hoy (según las keywords).")
        return

    # 2. PROCESAMIENTO: Aplicamos la clasificación teórica
    print(f"🚨 Analizando {len(df_sospechosos)} normas sospechosas...")
    df_sospechosos['Tipo_Fenomeno'] = df_sospechosos['Detalle'].apply(clasificar_fenomeno)

    # 3. ESTADÍSTICAS
    top_organismos = df_sospechosos['Organismo'].value_counts().head(5)
    top_mecanismos = df_sospechosos['Tipo_Fenomeno'].value_counts()

    # 4. REPORTE EN CONSOLA
    print("\n" + "="*50)
    print(f"📊 REPORTE DE FENÓMENOS CORRUPTIVOS - {FECHA_HOY}")
    print("="*50)

    print("\n🏆 Top 5 Organismos que más publicaron normas de alerta:")
    print(top_organismos)

    print("\n⚙️ Mecanismos de Transferencia Detectados:")
    print(top_mecanismos)

    print("\n👁️ Muestra de casos detectados:")
    pd.set_option('display.max_colwidth', 100)
    print(df_sospechosos[['Organismo', 'Tipo_Fenomeno', 'Detalle']].head(5))

    # 5. GUARDAR RESULTADO PROCESADO
    output_file = f"data/reporte_procesado_{FECHA_HOY}.xlsx"
    try:
        df_sospechosos.to_excel(output_file, index=False)
        print(f"\n💾 Reporte detallado guardado en Excel: {output_file}")
    except:
        # Si falla Excel (por falta de librería openpyxl), guardar CSV
        output_file = f"data/reporte_procesado_{FECHA_HOY}.csv"
        df_sospechosos.to_csv(output_file, index=False)
        print(f"\n💾 Reporte detallado guardado en CSV: {output_file}")

    # 6. GRÁFICO (Opcional)
    try:
        plt.figure(figsize=(10, 6))
        top_mecanismos.plot(kind='barh', color='darkred')
        plt.title(f'Fenómenos Corruptivos por Tipo ({FECHA_HOY})')
        plt.xlabel('Cantidad de Normas')
        plt.tight_layout()
        plt.savefig(f"data/grafico_{FECHA_HOY}.png")
        print("📈 Gráfico generado.")
    except Exception as e:
        print(f"No se pudo generar gráfico: {e}")

if __name__ == "__main__":
    analizar_boletin()