import pandas as pd
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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

def calculate_monthly_energy_costs(df_list: List[pd.DataFrame]):
    """
    Calcula los costos energéticos mensuales
    """
    # Parámetros del sistema actual
    num_robots = 25
    consumption_per_robot = 0.2
    total_consumption_per_hour = num_robots * consumption_per_robot
    working_hours_start = 8
    working_hours_end = 20
    
    monthly_costs = []
    monthly_details = []
    
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    for month_idx, df in enumerate(df_list):
        if df.empty:
            monthly_costs.append(0)
            monthly_details.append({
                'mes': months[month_idx],
                'costo_energia': 0,
                'precio_promedio': 0,
                'precio_minimo': 0,
                'precio_maximo': 0
            })
            continue
        
        # Extraer precios del horario laboral (filas 8-19)
        working_hours_prices = df.iloc[working_hours_start:working_hours_end]
        
        # Calcular costo mensual
        daily_costs = []
        all_prices = []
        
        for day in working_hours_prices.columns:
            day_prices = working_hours_prices[day].dropna()
            if len(day_prices) > 0:
                daily_cost = sum(price * total_consumption_per_hour for price in day_prices)
                daily_costs.append(daily_cost)
                all_prices.extend(day_prices)
        
        month_cost = sum(daily_costs)
        monthly_costs.append(month_cost)
        
        # Detalles del mes
        monthly_details.append({
            'mes': months[month_idx],
            'costo_energia': month_cost,
            'precio_promedio': np.mean(all_prices) if all_prices else 0,
            'precio_minimo': np.min(all_prices) if all_prices else 0,
            'precio_maximo': np.max(all_prices) if all_prices else 0
        })
    
    return monthly_costs, monthly_details

def calculate_monthly_revenues():
    """
    Calcula los ingresos mensuales (constantes para cada mes)
    """
    # Parámetros de producción
    num_robots = 25
    working_hours_per_day = 12
    
    # Productos por hora por robot
    minutes_per_product = 15
    products_per_robot_per_hour = 60 / minutes_per_product  # 4 productos/hora
    
    # Productos por día
    products_per_day = num_robots * working_hours_per_day * products_per_robot_per_hour
    
    # Ganancia promedio por producto (Grupo Impar) - 405 GTQ
    avg_profit_per_product_gtq = 405
    gtq_to_usd_rate = 7.8
    avg_profit_per_product_usd = avg_profit_per_product_gtq / gtq_to_usd_rate
    
    # Días por mes (aproximado)
    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    monthly_revenues = []
    for days in days_per_month:
        monthly_revenue = products_per_day * days * avg_profit_per_product_usd
        monthly_revenues.append(monthly_revenue)
    
    return monthly_revenues

def create_monthly_profitability_analysis(df_list: List[pd.DataFrame]):
    """
    Análisis completo de rentabilidad mensual con tabla y gráficas
    """
    print("="*80)
    print("ANÁLISIS DE RENTABILIDAD MENSUAL - 2023")
    print("="*80)
    
    # Calcular costos e ingresos mensuales
    monthly_costs, cost_details = calculate_monthly_energy_costs(df_list)
    monthly_revenues = calculate_monthly_revenues()
    
    # Calcular utilidades mensuales
    monthly_profits = [revenue - cost for revenue, cost in zip(monthly_revenues, monthly_costs)]
    
    # Crear DataFrame para análisis
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    df_analysis = pd.DataFrame({
        'Mes': months,
        'Mes_Num': range(1, 13),
        'Ingresos_USD': monthly_revenues,
        'Costos_Energia_USD': monthly_costs,
        'Utilidad_USD': monthly_profits,
        'Precio_Promedio_MWh': [detail['precio_promedio'] for detail in cost_details],
        'Precio_Min_MWh': [detail['precio_minimo'] for detail in cost_details],
        'Precio_Max_MWh': [detail['precio_maximo'] for detail in cost_details]
    })
    
    # Calcular métricas adicionales
    df_analysis['Margen_Utilidad_Pct'] = (df_analysis['Utilidad_USD'] / df_analysis['Ingresos_USD']) * 100
    df_analysis['ROI_Pct'] = (df_analysis['Utilidad_USD'] / df_analysis['Costos_Energia_USD']) * 100
    
    # Identificar mes más y menos rentable
    mes_mas_rentable = df_analysis.loc[df_analysis['Utilidad_USD'].idxmax()]
    mes_menos_rentable = df_analysis.loc[df_analysis['Utilidad_USD'].idxmin()]
    
    # TABLA COMPARATIVA MENSUAL
    print("\\nTABLA COMPARATIVA MENSUAL DE RENTABILIDAD")
    print("="*120)
    
    # Formatear tabla para mejor visualización
    table_df = df_analysis.copy()
    table_df['Ingresos_USD'] = table_df['Ingresos_USD'].apply(lambda x: f"${x:,.0f}")
    table_df['Costos_Energia_USD'] = table_df['Costos_Energia_USD'].apply(lambda x: f"${x:,.0f}")
    table_df['Utilidad_USD'] = table_df['Utilidad_USD'].apply(lambda x: f"${x:,.0f}")
    table_df['Precio_Promedio_MWh'] = table_df['Precio_Promedio_MWh'].apply(lambda x: f"${x:.2f}")
    table_df['Margen_Utilidad_Pct'] = table_df['Margen_Utilidad_Pct'].apply(lambda x: f"{x:.1f}%")
    table_df['ROI_Pct'] = table_df['ROI_Pct'].apply(lambda x: f"{x:.0f}%")
    
    # Mostrar tabla
    print(f"{'Mes':<12} {'Ingresos':<15} {'Costos Energía':<15} {'Utilidad':<15} {'Precio Prom':<12} {'Margen':<8} {'ROI':<6}")
    print("-" * 120)
    
    for _, row in table_df.iterrows():
        print(f"{row['Mes']:<12} {row['Ingresos_USD']:<15} {row['Costos_Energia_USD']:<15} "
              f"{row['Utilidad_USD']:<15} {row['Precio_Promedio_MWh']:<12} {row['Margen_Utilidad_Pct']:<8} {row['ROI_Pct']:<6}")
    
    # ESTADÍSTICAS CLAVE
    print("\\n" + "="*80)
    print("ESTADÍSTICAS CLAVE")
    print("="*80)
    
    total_ingresos = df_analysis['Ingresos_USD'].sum()
    total_costos = df_analysis['Costos_Energia_USD'].sum()
    total_utilidad = df_analysis['Utilidad_USD'].sum()
    
    print(f"\\nResumen Anual:")
    print(f"- Ingresos totales: ${total_ingresos:,.2f} USD")
    print(f"- Costos energéticos totales: ${total_costos:,.2f} USD")
    print(f"- Utilidad total: ${total_utilidad:,.2f} USD")
    print(f"- Margen de utilidad promedio: {(total_utilidad/total_ingresos)*100:.1f}%")
    
    print(f"\\nMes MÁS rentable:")
    print(f"- {mes_mas_rentable['Mes']}: ${mes_mas_rentable['Utilidad_USD']:,.2f} USD")
    print(f"- Precio promedio energía: ${mes_mas_rentable['Precio_Promedio_MWh']:.2f} USD/MWh")
    print(f"- Margen de utilidad: {mes_mas_rentable['Margen_Utilidad_Pct']:.1f}%")
    
    print(f"\\nMes MENOS rentable:")
    print(f"- {mes_menos_rentable['Mes']}: ${mes_menos_rentable['Utilidad_USD']:,.2f} USD")
    print(f"- Precio promedio energía: ${mes_menos_rentable['Precio_Promedio_MWh']:.2f} USD/MWh")
    print(f"- Margen de utilidad: {mes_menos_rentable['Margen_Utilidad_Pct']:.1f}%")
    
    diferencia_rentabilidad = mes_mas_rentable['Utilidad_USD'] - mes_menos_rentable['Utilidad_USD']
    print(f"\\nDiferencia de rentabilidad: ${diferencia_rentabilidad:,.2f} USD ({(diferencia_rentabilidad/mes_menos_rentable['Utilidad_USD'])*100:.1f}% más)")
    
    # CREAR GRÁFICAS
    create_profitability_charts(df_analysis)
    
    return df_analysis, mes_mas_rentable, mes_menos_rentable

def create_profitability_charts(df_analysis):
    """
    Crear gráficas de rentabilidad mensual
    """
    # Configurar estilo
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 15))
    
    # Colores personalizados
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # Gráfica 1: Evolución mensual de Ingresos, Costos y Utilidad
    ax1 = plt.subplot(2, 3, 1)
    x = df_analysis['Mes_Num']
    plt.plot(x, df_analysis['Ingresos_USD']/1000, marker='o', linewidth=3, 
             label='Ingresos', color=colors[0], markersize=8)
    plt.plot(x, df_analysis['Costos_Energia_USD']/1000, marker='s', linewidth=3, 
             label='Costos Energía', color=colors[1], markersize=8)
    plt.plot(x, df_analysis['Utilidad_USD']/1000, marker='^', linewidth=3, 
             label='Utilidad', color=colors[2], markersize=8)
    
    plt.title('Evolución Mensual de Rentabilidad\\n(Miles de USD)', fontsize=14, fontweight='bold')
    plt.xlabel('Mes', fontweight='bold')
    plt.ylabel('Miles USD', fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(x, [m[:3] for m in df_analysis['Mes']], rotation=45)
    
    # Gráfica 2: Utilidad mensual con barras
    ax2 = plt.subplot(2, 3, 2)
    bars = plt.bar(x, df_analysis['Utilidad_USD']/1000, color=colors[2], alpha=0.8, edgecolor='black')
    
    # Destacar mes más y menos rentable
    max_idx = df_analysis['Utilidad_USD'].idxmax()
    min_idx = df_analysis['Utilidad_USD'].idxmin()
    bars[max_idx].set_color('#4CAF50')  # Verde para el mejor
    bars[min_idx].set_color('#F44336')  # Rojo para el peor
    
    plt.title('Utilidad por Mes\\n(Verde: Mejor, Rojo: Peor)', fontsize=14, fontweight='bold')
    plt.xlabel('Mes', fontweight='bold')
    plt.ylabel('Utilidad (Miles USD)', fontweight='bold')
    plt.xticks(x, [m[:3] for m in df_analysis['Mes']], rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Añadir valores en las barras
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.0f}k', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Gráfica 3: Precios promedio de energía
    ax3 = plt.subplot(2, 3, 3)
    plt.plot(x, df_analysis['Precio_Promedio_MWh'], marker='o', linewidth=3, 
             color=colors[1], markersize=8)
    plt.fill_between(x, df_analysis['Precio_Promedio_MWh'], alpha=0.3, color=colors[1])
    
    plt.title('Precio Promedio de Energía\\nPor Mes (USD/MWh)', fontsize=14, fontweight='bold')
    plt.xlabel('Mes', fontweight='bold')
    plt.ylabel('USD/MWh', fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(x, [m[:3] for m in df_analysis['Mes']], rotation=45)
    
    # Gráfica 4: Margen de utilidad
    ax4 = plt.subplot(2, 3, 4)
    bars2 = plt.bar(x, df_analysis['Margen_Utilidad_Pct'], color=colors[0], alpha=0.8, edgecolor='black')
    
    plt.title('Margen de Utilidad por Mes\\n(%)', fontsize=14, fontweight='bold')
    plt.xlabel('Mes', fontweight='bold')
    plt.ylabel('Margen (%)', fontweight='bold')
    plt.xticks(x, [m[:3] for m in df_analysis['Mes']], rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 5: Correlación Precio vs Utilidad
    ax5 = plt.subplot(2, 3, 5)
    scatter = plt.scatter(df_analysis['Precio_Promedio_MWh'], df_analysis['Utilidad_USD']/1000, 
                         c=df_analysis['Mes_Num'], cmap='viridis', s=100, alpha=0.8, edgecolors='black')
    
    # Añadir etiquetas de mes
    for i, mes in enumerate(df_analysis['Mes']):
        plt.annotate(mes[:3], (df_analysis['Precio_Promedio_MWh'].iloc[i], 
                              df_analysis['Utilidad_USD'].iloc[i]/1000),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.title('Correlación: Precio Energía vs Utilidad', fontsize=14, fontweight='bold')
    plt.xlabel('Precio Promedio Energía (USD/MWh)', fontweight='bold')
    plt.ylabel('Utilidad (Miles USD)', fontweight='bold')
    plt.colorbar(scatter, label='Mes')
    plt.grid(True, alpha=0.3)
    
    # Gráfica 6: ROI mensual
    ax6 = plt.subplot(2, 3, 6)
    plt.plot(x, df_analysis['ROI_Pct'], marker='D', linewidth=3, 
             color=colors[3], markersize=8)
    plt.fill_between(x, df_analysis['ROI_Pct'], alpha=0.3, color=colors[3])
    
    plt.title('ROI Mensual\\n(%)', fontsize=14, fontweight='bold')
    plt.xlabel('Mes', fontweight='bold')
    plt.ylabel('ROI (%)', fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(x, [m[:3] for m in df_analysis['Mes']], rotation=45)
    
    plt.tight_layout()
    plt.savefig('rentabilidad_mensual_2023.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\\n📊 Gráficas guardadas como 'rentabilidad_mensual_2023.png'")

# Ejecutar análisis
file_path = r"Modela1Fixeddata.xlsx"
df_list: List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

# Realizar análisis de rentabilidad mensual
print("Iniciando análisis de rentabilidad mensual...")
resultado_mensual, mejor_mes, peor_mes = create_monthly_profitability_analysis(df_list)

print("\\n" + "="*80)
print("RESUMEN EJECUTIVO")
print("="*80)
print(f"✅ MES MÁS RENTABLE: {mejor_mes['Mes']} con ${mejor_mes['Utilidad_USD']:,.2f} USD")
print(f"❌ MES MENOS RENTABLE: {peor_mes['Mes']} con ${peor_mes['Utilidad_USD']:,.2f} USD")
print(f"📈 VARIACIÓN: {((mejor_mes['Utilidad_USD'] - peor_mes['Utilidad_USD'])/peor_mes['Utilidad_USD']*100):.1f}% de diferencia")
print("="*80)