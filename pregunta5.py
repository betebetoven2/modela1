import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
import calendar
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

def read_excel_sheets_to_dataframes(file_path):
    """
    Read Excel file with sheets named 1-12 and return list of DataFrames
    """
    dataframes = []
    
    for sheet_num in range(1, 13):
        try:
            df = pd.read_excel(file_path, sheet_name=str(sheet_num))
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading sheet '{sheet_num}': {e}")
            dataframes.append(pd.DataFrame())
    
    return dataframes

def create_guatemala_calendar_2023():
    """
    Crear calendario completo de Guatemala 2023 con todas las variables contextuales
    """
    
    # Días feriados oficiales de Guatemala 2023
    feriados_guatemala_2023 = [
        (1, 1),   # Año Nuevo
        (4, 6),   # Jueves Santo (abril 6, 2023)
        (4, 7),   # Viernes Santo
        (5, 1),   # Día del Trabajo
        (6, 30),  # Día del Ejército
        (9, 15),  # Día de la Independencia
        (10, 20), # Día de la Revolución
        (11, 1),  # Día de Todos los Santos
        (12, 24), # Nochebuena
        (12, 25), # Navidad
        (12, 31), # Fin de Año
    ]
    
    # Períodos escolares en Guatemala 2023 (aproximados)
    # Ciclo escolar: Enero-Octubre (con vacaciones en julio)
    periodos_escolares = [
        (1, 1, 6, 30),    # Primer semestre: Enero-Junio
        (8, 1, 10, 31),   # Segundo semestre: Agosto-Octubre
    ]
    
    # Crear DataFrame con todos los días del año
    year = 2023
    calendar_data = []
    
    for month in range(1, 13):
        days_in_month = calendar.monthrange(year, month)[1]
        
        for day in range(1, days_in_month + 1):
            fecha = date(year, month, day)
            
            # Información básica
            dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
            nombre_dia = calendar.day_name[dia_semana]
            
            # Clasificaciones
            es_fin_de_semana = dia_semana >= 5  # Sábado=5, Domingo=6
            es_semana_laboral = dia_semana < 4  # Lunes-Jueves
            es_viernes = dia_semana == 4
            
            # Estación del año (Hemisferio Norte - Guatemala)
            if month in [12, 1, 2]:
                estacion = 'Invierno'
            elif month in [3, 4, 5]:
                estacion = 'Primavera'
            elif month in [6, 7, 8]:
                estacion = 'Verano'
            else:  # 9, 10, 11
                estacion = 'Otoño'
            
            # Días feriados
            es_feriado = (month, day) in feriados_guatemala_2023
            
            # Ciclo escolar activo
            ciclo_escolar_activo = False
            for inicio_mes, inicio_dia, fin_mes, fin_dia in periodos_escolares:
                inicio_periodo = date(year, inicio_mes, inicio_dia)
                fin_periodo = date(year, fin_mes, fin_dia)
                if inicio_periodo <= fecha <= fin_periodo:
                    ciclo_escolar_activo = True
                    break
            
            # Clasificación especial
            if es_feriado:
                clasificacion = 'Feriado'
            elif es_fin_de_semana:
                clasificacion = 'Fin de Semana'
            elif es_semana_laboral:
                clasificacion = 'Semana Laboral'
            elif es_viernes:
                clasificacion = 'Viernes'
            else:
                clasificacion = 'Otro'
            
            calendar_data.append({
                'fecha': fecha,
                'año': year,
                'mes': month,
                'dia': day,
                'dia_semana_num': dia_semana,
                'dia_semana_nombre': nombre_dia,
                'es_fin_de_semana': es_fin_de_semana,
                'es_semana_laboral': es_semana_laboral,
                'es_viernes': es_viernes,
                'es_feriado': es_feriado,
                'estacion': estacion,
                'ciclo_escolar_activo': ciclo_escolar_activo,
                'clasificacion': clasificacion
            })
    
    return pd.DataFrame(calendar_data)

def map_energy_data_with_context(df_list, calendar_df):
    """
    Mapear datos energéticos con variables contextuales
    """
    energy_context_data = []
    
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    for month_idx, df in enumerate(df_list):
        if df.empty:
            continue
            
        month_num = month_idx + 1
        month_calendar = calendar_df[calendar_df['mes'] == month_num].copy()
        
        # Para cada día del mes
        for day_idx, column in enumerate(df.columns):
            if day_idx < len(month_calendar):
                day_info = month_calendar.iloc[day_idx]
                
                # Para cada hora del día
                for hour in range(24):
                    if hour < len(df):
                        precio = df.iloc[hour, day_idx]
                        
                        if pd.notna(precio):
                            energy_context_data.append({
                                'fecha': day_info['fecha'],
                                'mes': month_num,
                                'mes_nombre': months[month_idx],
                                'dia': day_info['dia'],
                                'hora': hour,
                                'precio_mwh': precio,
                                'dia_semana_num': day_info['dia_semana_num'],
                                'dia_semana_nombre': day_info['dia_semana_nombre'],
                                'es_fin_de_semana': day_info['es_fin_de_semana'],
                                'es_semana_laboral': day_info['es_semana_laboral'],
                                'es_viernes': day_info['es_viernes'],
                                'es_feriado': day_info['es_feriado'],
                                'estacion': day_info['estacion'],
                                'ciclo_escolar_activo': day_info['ciclo_escolar_activo'],
                                'clasificacion': day_info['clasificacion']
                            })
    
    return pd.DataFrame(energy_context_data)

def comprehensive_energy_analysis(df_list):
    """
    Análisis integral de datos energéticos con variables contextuales
    """
    print("="*100)
    print("ANÁLISIS INTEGRAL DE DATOS ENERGÉTICOS CON VARIABLES CONTEXTUALES")
    print("Guatemala 2023")
    print("="*100)
    
    # Crear calendario contextual
    print("\\n📅 Creando calendario contextual de Guatemala 2023...")
    calendar_df = create_guatemala_calendar_2023()
    
    # Mapear datos energéticos con contexto
    print("🔗 Mapeando datos energéticos con variables contextuales...")
    energy_context_df = map_energy_data_with_context(df_list, calendar_df)
    
    print(f"✅ Datos procesados: {len(energy_context_df):,} registros hora-día")
    
    # ANÁLISIS POR DÍA DE LA SEMANA
    print("\\n" + "="*80)
    print("ANÁLISIS POR DÍA DE LA SEMANA")
    print("="*80)
    
    weekday_analysis = energy_context_df.groupby('dia_semana_nombre').agg({
        'precio_mwh': ['mean', 'std', 'min', 'max', 'count']
    }).round(2)
    weekday_analysis.columns = ['Precio_Promedio', 'Desviacion_Std', 'Precio_Min', 'Precio_Max', 'Registros']
    weekday_analysis = weekday_analysis.sort_values('Precio_Promedio')
    
    print("\\nPrecios promedio por día de la semana (USD/MWh):")
    print(weekday_analysis)
    
    dia_mas_barato = weekday_analysis.index[0]
    dia_mas_caro = weekday_analysis.index[-1]
    
    print(f"\\n🟢 Día MÁS BARATO: {dia_mas_barato} (${weekday_analysis.loc[dia_mas_barato, 'Precio_Promedio']:.2f}/MWh)")
    print(f"🔴 Día MÁS CARO: {dia_mas_caro} (${weekday_analysis.loc[dia_mas_caro, 'Precio_Promedio']:.2f}/MWh)")
    
    # ANÁLISIS POR CLASIFICACIÓN
    print("\\n" + "="*80)
    print("ANÁLISIS POR CLASIFICACIÓN DE DÍAS")
    print("="*80)
    
    classification_analysis = energy_context_df.groupby('clasificacion').agg({
        'precio_mwh': ['mean', 'std', 'count']
    }).round(2)
    classification_analysis.columns = ['Precio_Promedio', 'Desviacion_Std', 'Registros']
    classification_analysis = classification_analysis.sort_values('Precio_Promedio')
    
    print("\\nPrecios promedio por clasificación:")
    print(classification_analysis)
    
    # ANÁLISIS POR ESTACIÓN
    print("\\n" + "="*80)
    print("ANÁLISIS POR ESTACIÓN DEL AÑO")
    print("="*80)
    
    season_analysis = energy_context_df.groupby('estacion').agg({
        'precio_mwh': ['mean', 'std', 'min', 'max', 'count']
    }).round(2)
    season_analysis.columns = ['Precio_Promedio', 'Desviacion_Std', 'Precio_Min', 'Precio_Max', 'Registros']
    season_analysis = season_analysis.sort_values('Precio_Promedio')
    
    print("\\nPrecios promedio por estación:")
    print(season_analysis)
    
    estacion_mas_barata = season_analysis.index[0]
    estacion_mas_cara = season_analysis.index[-1]
    
    print(f"\\n🌿 Estación MÁS BARATA: {estacion_mas_barata} (${season_analysis.loc[estacion_mas_barata, 'Precio_Promedio']:.2f}/MWh)")
    print(f"🌡️  Estación MÁS CARA: {estacion_mas_cara} (${season_analysis.loc[estacion_mas_cara, 'Precio_Promedio']:.2f}/MWh)")
    
    # ANÁLISIS CICLO ESCOLAR
    print("\\n" + "="*80)
    print("ANÁLISIS CICLO ESCOLAR")
    print("="*80)
    
    school_analysis = energy_context_df.groupby('ciclo_escolar_activo').agg({
        'precio_mwh': ['mean', 'std', 'count']
    }).round(2)
    school_analysis.columns = ['Precio_Promedio', 'Desviacion_Std', 'Registros']
    school_analysis.index = ['Vacaciones Escolares', 'Ciclo Escolar Activo']
    
    print("\\nPrecios promedio según ciclo escolar:")
    print(school_analysis)
    
    # ANÁLISIS DE FERIADOS
    print("\\n" + "="*80)
    print("ANÁLISIS DE DÍAS FERIADOS")
    print("="*80)
    
    holiday_analysis = energy_context_df.groupby('es_feriado').agg({
        'precio_mwh': ['mean', 'std', 'count']
    }).round(2)
    holiday_analysis.columns = ['Precio_Promedio', 'Desviacion_Std', 'Registros']
    holiday_analysis.index = ['Días Regulares', 'Días Feriados']
    
    print("\\nPrecios promedio en días feriados vs regulares:")
    print(holiday_analysis)
    
    # ANÁLISIS POR HORA Y CONTEXTO
    print("\\n" + "="*80)
    print("ANÁLISIS COMBINADO: HORA + CONTEXTO")
    print("="*80)
    
    # Mejores y peores horarios por tipo de día
    best_hours_by_type = {}
    
    for tipo in energy_context_df['clasificacion'].unique():
        tipo_data = energy_context_df[energy_context_df['clasificacion'] == tipo]
        hourly_avg = tipo_data.groupby('hora')['precio_mwh'].mean().sort_values()
        
        best_hours_by_type[tipo] = {
            'mejor_hora': hourly_avg.index[0],
            'mejor_precio': hourly_avg.iloc[0],
            'peor_hora': hourly_avg.index[-1],
            'peor_precio': hourly_avg.iloc[-1]
        }
    
    print("\\nMejores y peores horas por tipo de día:")
    for tipo, data in best_hours_by_type.items():
        print(f"\\n{tipo}:")
        print(f"  🟢 Mejor hora: {data['mejor_hora']:02d}:00 (${data['mejor_precio']:.2f}/MWh)")
        print(f"  🔴 Peor hora: {data['peor_hora']:02d}:00 (${data['peor_precio']:.2f}/MWh)")
    
    # CREAR GRÁFICAS AVANZADAS
    create_comprehensive_charts(energy_context_df)
    
    # RECOMENDACIONES ESTRATÉGICAS
    generate_strategic_recommendations(energy_context_df, weekday_analysis, season_analysis, best_hours_by_type)
    
    # ANÁLISIS DE OPORTUNIDADES
    identify_optimization_opportunities(energy_context_df)
    
    return energy_context_df, calendar_df

def create_comprehensive_charts(energy_context_df):
    """
    Crear gráficas comprehensivas del análisis
    """
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(24, 16))
    
    # Paleta de colores personalizada
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#4CAF50', '#9C27B0']
    
    # Gráfica 1: Precios por día de la semana
    ax1 = plt.subplot(3, 4, 1)
    weekday_avg = energy_context_df.groupby('dia_semana_nombre')['precio_mwh'].mean().sort_values()
    bars1 = plt.bar(range(len(weekday_avg)), weekday_avg.values, color=colors[0], alpha=0.8)
    plt.title('Precio Promedio por Día\\nde la Semana', fontsize=12, fontweight='bold')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Precio (USD/MWh)')
    plt.xticks(range(len(weekday_avg)), [day[:3] for day in weekday_avg.index], rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 2: Precios por estación
    ax2 = plt.subplot(3, 4, 2)
    season_avg = energy_context_df.groupby('estacion')['precio_mwh'].mean().sort_values()
    bars2 = plt.bar(range(len(season_avg)), season_avg.values, color=colors[1], alpha=0.8)
    plt.title('Precio Promedio por\\nEstación del Año', fontsize=12, fontweight='bold')
    plt.xlabel('Estación')
    plt.ylabel('Precio (USD/MWh)')
    plt.xticks(range(len(season_avg)), season_avg.index, rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 3: Heatmap hora vs día de semana
    ax3 = plt.subplot(3, 4, 3)
    pivot_data = energy_context_df.pivot_table(values='precio_mwh', 
                                              index='hora', 
                                              columns='dia_semana_nombre', 
                                              aggfunc='mean')
    
    # Reordenar columnas para que empiecen en lunes
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_data = pivot_data.reindex(columns=day_order)
    
    sns.heatmap(pivot_data, cmap='RdYlBu_r', cbar_kws={'label': 'Precio (USD/MWh)'}, 
                fmt='.1f', linewidths=0.1)
    plt.title('Heatmap: Hora vs Día\\nde la Semana', fontsize=12, fontweight='bold')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Hora del Día')
    plt.xticks(range(len(day_order)), [day[:3] for day in day_order])
    
    # Gráfica 4: Clasificación de días
    ax4 = plt.subplot(3, 4, 4)
    classification_avg = energy_context_df.groupby('clasificacion')['precio_mwh'].mean().sort_values()
    bars4 = plt.bar(range(len(classification_avg)), classification_avg.values, color=colors[2], alpha=0.8)
    plt.title('Precio por Clasificación\\nde Días', fontsize=12, fontweight='bold')
    plt.xlabel('Clasificación')
    plt.ylabel('Precio (USD/MWh)')
    plt.xticks(range(len(classification_avg)), classification_avg.index, rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 5: Evolución mensual con contexto
    ax5 = plt.subplot(3, 4, 5)
    monthly_avg = energy_context_df.groupby('mes')['precio_mwh'].mean()
    monthly_escolar = energy_context_df.groupby(['mes', 'ciclo_escolar_activo'])['precio_mwh'].mean().unstack()
    
    if True in monthly_escolar.columns and False in monthly_escolar.columns:
        plt.plot(monthly_avg.index, monthly_escolar[True], 'o-', label='Ciclo Escolar', color=colors[3], linewidth=2)
        plt.plot(monthly_avg.index, monthly_escolar[False], 's-', label='Vacaciones', color=colors[4], linewidth=2)
        plt.legend()
    else:
        plt.plot(monthly_avg.index, monthly_avg.values, 'o-', color=colors[3], linewidth=2)
    
    plt.title('Evolución Mensual\\nCiclo Escolar vs Vacaciones', fontsize=12, fontweight='bold')
    plt.xlabel('Mes')
    plt.ylabel('Precio (USD/MWh)')
    plt.xticks(range(1, 13))
    plt.grid(True, alpha=0.3)
    
    # Gráfica 6: Boxplot por estación
    ax6 = plt.subplot(3, 4, 6)
    seasons_order = ['Invierno', 'Primavera', 'Verano', 'Otoño']
    season_data = [energy_context_df[energy_context_df['estacion'] == season]['precio_mwh'].values 
                   for season in seasons_order]
    
    box_plot = plt.boxplot(season_data, labels=[s[:3] for s in seasons_order], patch_artist=True)
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    plt.title('Distribución de Precios\\npor Estación', fontsize=12, fontweight='bold')
    plt.xlabel('Estación')
    plt.ylabel('Precio (USD/MWh)')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 7: Feriados vs días regulares
    ax7 = plt.subplot(3, 4, 7)
    holiday_comparison = energy_context_df.groupby(['hora', 'es_feriado'])['precio_mwh'].mean().unstack()
    
    if True in holiday_comparison.columns and False in holiday_comparison.columns:
        plt.plot(holiday_comparison.index, holiday_comparison[False], 'o-', 
                label='Días Regulares', color=colors[0], linewidth=2)
        plt.plot(holiday_comparison.index, holiday_comparison[True], 's-', 
                label='Días Feriados', color=colors[1], linewidth=2)
        plt.legend()
    
    plt.title('Precios: Feriados vs\\nDías Regulares', fontsize=12, fontweight='bold')
    plt.xlabel('Hora del Día')
    plt.ylabel('Precio (USD/MWh)')
    plt.grid(True, alpha=0.3)
    
    # Gráfica 8: Fin de semana vs semana laboral
    ax8 = plt.subplot(3, 4, 8)
    weekend_comparison = energy_context_df.groupby(['hora', 'es_fin_de_semana'])['precio_mwh'].mean().unstack()
    
    if True in weekend_comparison.columns and False in weekend_comparison.columns:
        plt.plot(weekend_comparison.index, weekend_comparison[False], 'o-', 
                label='Días Laborales', color=colors[2], linewidth=2)
        plt.plot(weekend_comparison.index, weekend_comparison[True], 's-', 
                label='Fin de Semana', color=colors[3], linewidth=2)
        plt.legend()
    
    plt.title('Precios: Fin de Semana vs\\nDías Laborales', fontsize=12, fontweight='bold')
    plt.xlabel('Hora del Día')
    plt.ylabel('Precio (USD/MWh)')
    plt.grid(True, alpha=0.3)
    
    # Gráfica 9: Heatmap estación vs hora
    ax9 = plt.subplot(3, 4, 9)
    season_hour_pivot = energy_context_df.pivot_table(values='precio_mwh', 
                                                     index='hora', 
                                                     columns='estacion', 
                                                     aggfunc='mean')
    
    sns.heatmap(season_hour_pivot, cmap='RdYlBu_r', cbar_kws={'label': 'Precio (USD/MWh)'}, 
                fmt='.1f', linewidths=0.1)
    plt.title('Heatmap: Hora vs\\nEstación', fontsize=12, fontweight='bold')
    plt.xlabel('Estación')
    plt.ylabel('Hora del Día')
    
    # Gráfica 10: Variabilidad por mes
    ax10 = plt.subplot(3, 4, 10)
    monthly_std = energy_context_df.groupby('mes')['precio_mwh'].std()
    plt.bar(monthly_std.index, monthly_std.values, color=colors[4], alpha=0.8)
    plt.title('Variabilidad de Precios\\npor Mes', fontsize=12, fontweight='bold')
    plt.xlabel('Mes')
    plt.ylabel('Desviación Estándar')
    plt.xticks(range(1, 13))
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 11: Correlación entre variables
    ax11 = plt.subplot(3, 4, 11)
    
    # Crear variables numéricas para correlación
    corr_data = energy_context_df[['precio_mwh', 'hora', 'mes', 'dia_semana_num']].copy()
    corr_data['es_fin_de_semana_num'] = energy_context_df['es_fin_de_semana'].astype(int)
    corr_data['es_feriado_num'] = energy_context_df['es_feriado'].astype(int)
    corr_data['ciclo_escolar_num'] = energy_context_df['ciclo_escolar_activo'].astype(int)
    
    correlation_matrix = corr_data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0, 
                fmt='.2f', linewidths=0.5)
    plt.title('Matriz de Correlación', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    
    # Gráfica 12: Top insights
    ax12 = plt.subplot(3, 4, 12)
    ax12.axis('off')
    
    # Calcular insights clave
    cheapest_day = energy_context_df.groupby('dia_semana_nombre')['precio_mwh'].mean().idxmin()
    cheapest_season = energy_context_df.groupby('estacion')['precio_mwh'].mean().idxmin()
    cheapest_hour = energy_context_df.groupby('hora')['precio_mwh'].mean().idxmin()
    
    insights_text = f'''INSIGHTS CLAVE
    
🟢 DÍA MÁS BARATO:
{cheapest_day}

🌿 ESTACIÓN MÁS BARATA:
{cheapest_season}

⏰ HORA MÁS BARATA:
{cheapest_hour:02d}:00

📊 REGISTROS TOTALES:
{len(energy_context_df):,}

🎯 OPORTUNIDAD:
Optimizar horarios según
patrones identificados'''
    
    plt.text(0.1, 0.9, insights_text, transform=ax12.transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('analisis_integral_energia_contexto.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\\n📊 Gráficas guardadas como 'analisis_integral_energia_contexto.png'")

def generate_strategic_recommendations(energy_context_df, weekday_analysis, season_analysis, best_hours_by_type):
    """
    Generar recomendaciones estratégicas basadas en el análisis integral
    """
    print("\\n" + "="*100)
    print("RECOMENDACIONES ESTRATÉGICAS BASADAS EN ANÁLISIS INTEGRAL")
    print("="*100)
    
    # Análisis de ahorro potencial
    precio_promedio_general = energy_context_df['precio_mwh'].mean()
    
    print(f"\\n🎯 OPTIMIZACIÓN TEMPORAL:")
    
    # Mejor día de la semana
    mejor_dia = weekday_analysis.index[0]
    peor_dia = weekday_analysis.index[-1]
    ahorro_dia = weekday_analysis.loc[peor_dia, 'Precio_Promedio'] - weekday_analysis.loc[mejor_dia, 'Precio_Promedio']
    
    print(f"\\n1. DÍA DE LA SEMANA:")
    print(f"   • Operar preferentemente en: {mejor_dia}")
    print(f"   • Evitar operaciones intensivas en: {peor_dia}")
    print(f"   • Ahorro potencial: ${ahorro_dia:.2f}/MWh ({(ahorro_dia/precio_promedio_general)*100:.1f}%)")
    
    # Mejor estación
    mejor_estacion = season_analysis.index[0]
    peor_estacion = season_analysis.index[-1]
    ahorro_estacion = season_analysis.loc[peor_estacion, 'Precio_Promedio'] - season_analysis.loc[mejor_estacion, 'Precio_Promedio']
    
    print(f"\\n2. ESTACIONALIDAD:")
    print(f"   • Temporada óptima: {mejor_estacion}")
    print(f"   • Temporada costosa: {peor_estacion}")
    print(f"   • Diferencia estacional: ${ahorro_estacion:.2f}/MWh ({(ahorro_estacion/precio_promedio_general)*100:.1f}%)")
    
    # Análisis de horarios óptimos por contexto
    print(f"\\n3. HORARIOS ÓPTIMOS POR CONTEXTO:")
    for tipo, data in best_hours_by_type.items():
        ahorro_horario = data['peor_precio'] - data['mejor_precio']
        print(f"\\n   {tipo}:")
        print(f"   • Mejor horario: {data['mejor_hora']:02d}:00 (${data['mejor_precio']:.2f}/MWh)")
        print(f"   • Peor horario: {data['peor_hora']:02d}:00 (${data['peor_precio']:.2f}/MWh)")
        print(f"   • Ahorro horario: ${ahorro_horario:.2f}/MWh ({(ahorro_horario/precio_promedio_general)*100:.1f}%)")

def identify_optimization_opportunities(energy_context_df):
    """
    Identificar oportunidades específicas de optimización
    """
    print("\\n" + "="*100)
    print("OPORTUNIDADES DE OPTIMIZACIÓN IDENTIFICADAS")
    print("="*100)
    
    # Calcular consumo actual del sistema
    num_robots = 25
    consumption_per_robot = 0.2
    total_consumption_per_hour = num_robots * consumption_per_robot
    
    # Análisis de oportunidades
    precio_promedio = energy_context_df['precio_mwh'].mean()
    
    # Oportunidad 1: Optimización por día de semana
    print("\\n💡 OPORTUNIDAD 1: OPTIMIZACIÓN POR DÍA DE SEMANA")
    weekday_savings = energy_context_df.groupby('dia_semana_nombre')['precio_mwh'].mean()
    mejor_dia_week = weekday_savings.idxmin()
    peor_dia_week = weekday_savings.idxmax()
    ahorro_semanal = (weekday_savings[peor_dia_week] - weekday_savings[mejor_dia_week]) * total_consumption_per_hour * 12  # 12 horas/día
    
    print(f"• Concentrar operaciones en {mejor_dia_week}")
    print(f"• Reducir operaciones en {peor_dia_week}")
    print(f"• Ahorro potencial: ${ahorro_semanal:.2f} USD por día de cambio")
    print(f"• Ahorro mensual estimado: ${ahorro_semanal * 4:.2f} USD")
    
    # Oportunidad 2: Horarios valle
    print("\\n💡 OPORTUNIDAD 2: APROVECHAMIENTO DE HORARIOS VALLE")
    hourly_avg = energy_context_df.groupby('hora')['precio_mwh'].mean().sort_values()
    top_5_cheapest = hourly_avg.head(5)
    top_5_expensive = hourly_avg.tail(5)
    
    print("\\nHorarios MÁS BARATOS (Valle):")
    for hora, precio in top_5_cheapest.items():
        print(f"  • {hora:02d}:00 - ${precio:.2f}/MWh")
    
    print("\\nHorarios MÁS CAROS (Pico):")
    for hora, precio in top_5_expensive.items():
        print(f"  • {hora:02d}:00 - ${precio:.2f}/MWh")
    
    ahorro_horario_max = top_5_expensive.mean() - top_5_cheapest.mean()
    ahorro_por_cambio_horario = ahorro_horario_max * total_consumption_per_hour
    
    print(f"\\n• Ahorro por cambiar de horario pico a valle: ${ahorro_por_cambio_horario:.2f} USD/hora")
    print(f"• Ahorro diario (12 horas): ${ahorro_por_cambio_horario * 12:.2f} USD")
    print(f"• Ahorro mensual: ${ahorro_por_cambio_horario * 12 * 30:.2f} USD")
    
    # Oportunidad 3: Estrategia estacional
    print("\\n💡 OPORTUNIDAD 3: ESTRATEGIA ESTACIONAL")
    seasonal_avg = energy_context_df.groupby('estacion')['precio_mwh'].mean()
    mejor_estacion = seasonal_avg.idxmin()
    peor_estacion = seasonal_avg.idxmax()
    
    print(f"• Incrementar producción en {mejor_estacion}: ${seasonal_avg[mejor_estacion]:.2f}/MWh")
    print(f"• Mantenimiento programado en {peor_estacion}: ${seasonal_avg[peor_estacion]:.2f}/MWh")
    
    # Oportunidad 4: Calendario inteligente
    print("\\n💡 OPORTUNIDAD 4: CALENDARIO OPERATIVO INTELIGENTE")
    
    # Días con mejores precios
    best_days_data = energy_context_df[energy_context_df['precio_mwh'] <= energy_context_df['precio_mwh'].quantile(0.25)]
    worst_days_data = energy_context_df[energy_context_df['precio_mwh'] >= energy_context_df['precio_mwh'].quantile(0.75)]
    
    print("\\nCaracterísticas de días con MEJORES precios:")
    best_day_chars = best_days_data.groupby(['dia_semana_nombre', 'es_feriado', 'estacion']).size().sort_values(ascending=False).head(3)
    for (dia, feriado, estacion), count in best_day_chars.items():
        feriado_text = "Feriado" if feriado else "Regular"
        print(f"  • {dia}, {feriado_text}, {estacion}: {count} registros")
    
    print("\\nCaracterísticas de días con PEORES precios:")
    worst_day_chars = worst_days_data.groupby(['dia_semana_nombre', 'es_feriado', 'estacion']).size().sort_values(ascending=False).head(3)
    for (dia, feriado, estacion), count in worst_day_chars.items():
        feriado_text = "Feriado" if feriado else "Regular"
        print(f"  • {dia}, {feriado_text}, {estacion}: {count} registros")
    
    # RESUMEN DE AHORROS
    print("\\n" + "="*100)
    print("RESUMEN DE AHORROS POTENCIALES")
    print("="*100)
    
    ahorro_total_mensual = (ahorro_semanal * 4) + (ahorro_por_cambio_horario * 12 * 30)
    ahorro_total_anual = ahorro_total_mensual * 12
    
    print(f"\\n💰 AHORROS ESTIMADOS:")
    print(f"• Optimización semanal: ${ahorro_semanal * 4:,.2f} USD/mes")
    print(f"• Optimización horaria: ${ahorro_por_cambio_horario * 12 * 30:,.2f} USD/mes")
    print(f"• TOTAL MENSUAL: ${ahorro_total_mensual:,.2f} USD")
    print(f"• TOTAL ANUAL: ${ahorro_total_anual:,.2f} USD")
    print(f"• Porcentaje de ahorro: {(ahorro_total_anual / (precio_promedio * total_consumption_per_hour * 12 * 365)) * 100:.1f}%")

# Ejecutar análisis integral
file_path = r"Modela1Fixeddata.xlsx"
df_list: List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

print("Iniciando análisis integral con variables contextuales...")
energy_context_data, calendar_data = comprehensive_energy_analysis(df_list)

print("\\n" + "="*100)
print("ANÁLISIS COMPLETADO EXITOSAMENTE")
print("="*100)
print("✅ Datos enriquecidos con variables contextuales")
print("📊 Gráficas avanzadas generadas") 
print("🎯 Recomendaciones estratégicas identificadas")
print("💡 Oportunidades de optimización cuantificadas")
print("="*100)