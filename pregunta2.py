import pandas as pd
from typing import List
import numpy as np

def read_excel_sheets_to_dataframes(file_path):
    """
    Read Excel file with sheets named 1-12 and return list of DataFrames
    """
    dataframes = []
    
    for sheet_num in range(1, 13):
        try:
            df = pd.read_excel(file_path, sheet_name=str(sheet_num))
            dataframes.append(df)
            print(f"Successfully read sheet '{sheet_num}' with shape {df.shape}")
        except Exception as e:
            print(f"Error reading sheet '{sheet_num}': {e}")
            dataframes.append(pd.DataFrame())
    
    return dataframes

def calculate_energy_cost_scenario(df_list: List[pd.DataFrame], 
                                 num_robots=25, 
                                 consumption_per_robot=0.2, 
                                 working_hours_start=8, 
                                 working_hours_end=20,
                                 scenario_name="Actual"):
    """
    Calcula el costo energético para un escenario específico
    """
    total_consumption_per_hour = num_robots * consumption_per_robot
    working_hours_per_day = working_hours_end - working_hours_start
    
    print(f"\n{'='*60}")
    print(f"ESCENARIO: {scenario_name}")
    print(f"{'='*60}")
    print(f"- Número de robots: {num_robots}")
    print(f"- Consumo por robot: {consumption_per_robot} MWh/hora")
    print(f"- Consumo total por hora: {total_consumption_per_hour} MWh/hora")
    print(f"- Horario de operación: {working_hours_start}:00 - {working_hours_end}:00")
    print(f"- Horas de trabajo por día: {working_hours_per_day}")
    
    monthly_costs = []
    
    for month_idx, df in enumerate(df_list):
        if df.empty:
            monthly_costs.append(0)
            continue
        
        # Extraer precios del horario laboral
        working_hours_prices = df.iloc[working_hours_start:working_hours_end]
        
        daily_costs = []
        for day in working_hours_prices.columns:
            day_prices = working_hours_prices[day].dropna()
            if len(day_prices) > 0:
                daily_cost = sum(price * total_consumption_per_hour for price in day_prices)
                daily_costs.append(daily_cost)
        
        month_cost = sum(daily_costs)
        monthly_costs.append(month_cost)
    
    total_annual_cost = sum(monthly_costs)
    return total_annual_cost, monthly_costs

def calculate_revenue_scenario(working_hours_per_day, scenario_name="Actual"):
    """
    Calcula los ingresos basados en el tiempo de trabajo y productos procesados
    """
    # Parámetros de producción
    num_robots = 25
    
    # Tiempos promedio por producto por robot (en minutos)
    # Recolección: 2 min, Descarga: 10 min, Transporte: 3 min = 15 min total
    minutes_per_product = 15
    products_per_robot_per_hour = 60 / minutes_per_product  # 4 productos/hora
    
    # Productos procesados por día
    products_per_day = num_robots * working_hours_per_day * products_per_robot_per_hour
    products_per_year = products_per_day * 365  # días laborales aproximados
    
    # Ganancias por producto (Grupo Impar) en quetzales
    product_profits = {
        'Equipos de Sonido y Video': 600,
        'Electrodomésticos': 450,
        'Adornos': 75,
        'Muebles': 900,
        'Productos para el hogar': 75
    }
    
    # Probabilidades (Grupo Impar)
    product_probabilities = {
        'Equipos de Sonido y Video': 0.10,
        'Electrodomésticos': 0.30,
        'Adornos': 0.20,
        'Muebles': 0.20,
        'Productos para el hogar': 0.20
    }
    
    # Calcular ganancia promedio por producto
    avg_profit_per_product = sum(profit * prob for profit, prob in 
                                zip(product_profits.values(), product_probabilities.values()))
    
    # Ingresos totales anuales
    total_annual_revenue_gtq = products_per_year * avg_profit_per_product
    
    # Conversión a USD (aproximada: 1 USD = 7.8 GTQ)
    gtq_to_usd_rate = 7.8
    total_annual_revenue_usd = total_annual_revenue_gtq / gtq_to_usd_rate
    
    print(f"\nCálculo de Ingresos - {scenario_name}:")
    print(f"- Productos por robot por hora: {products_per_robot_per_hour:.1f}")
    print(f"- Productos procesados por día: {products_per_day:.0f}")
    print(f"- Productos procesados por año: {products_per_year:.0f}")
    print(f"- Ganancia promedio por producto: {avg_profit_per_product:.0f} GTQ")
    print(f"- Ingresos anuales: {total_annual_revenue_gtq:,.0f} GTQ")
    print(f"- Ingresos anuales: ${total_annual_revenue_usd:,.2f} USD")
    
    return total_annual_revenue_usd, products_per_year

def profitability_analysis(df_list: List[pd.DataFrame]):
    """
    Análisis completo de rentabilidad comparando escenarios
    """
    print("="*80)
    print("ANÁLISIS DE RENTABILIDAD - COMPARACIÓN DE ESCENARIOS")
    print("="*80)
    
    # ESCENARIO ACTUAL
    print("\n" + "="*60)
    print("ESCENARIO ACTUAL")
    print("="*60)
    
    current_energy_cost, _ = calculate_energy_cost_scenario(
        df_list, 
        num_robots=25,
        consumption_per_robot=0.2,
        working_hours_start=8,
        working_hours_end=20,
        scenario_name="Actual"
    )
    
    current_revenue, current_products = calculate_revenue_scenario(
        working_hours_per_day=12, 
        scenario_name="Actual"
    )
    
    current_profit = current_revenue - current_energy_cost
    
    # ESCENARIO MODIFICADO
    print("\n" + "="*60)
    print("ESCENARIO MODIFICADO")
    print("="*60)
    
    # Trabajar la mitad del tiempo: 6 horas centrales (10:00-16:00)
    modified_energy_cost, _ = calculate_energy_cost_scenario(
        df_list,
        num_robots=25,
        consumption_per_robot=0.15,  # Menor consumo
        working_hours_start=10,      # 6 horas centrales
        working_hours_end=16,
        scenario_name="Modificado"
    )
    
    modified_revenue, modified_products = calculate_revenue_scenario(
        working_hours_per_day=6,
        scenario_name="Modificado"
    )
    
    modified_profit = modified_revenue - modified_energy_cost
    
    # COMPARACIÓN Y ANÁLISIS
    print("\n" + "="*80)
    print("COMPARACIÓN DE ESCENARIOS")
    print("="*80)
    
    print(f"\n{'Métrica':<30} {'Actual':<20} {'Modificado':<20} {'Diferencia':<15}")
    print("-" * 85)
    print(f"{'Costo Energético (USD)':<30} ${current_energy_cost:>15,.2f} ${modified_energy_cost:>15,.2f} ${modified_energy_cost - current_energy_cost:>12,.2f}")
    print(f"{'Ingresos (USD)':<30} ${current_revenue:>15,.2f} ${modified_revenue:>15,.2f} ${modified_revenue - current_revenue:>12,.2f}")
    print(f"{'Utilidad (USD)':<30} ${current_profit:>15,.2f} ${modified_profit:>15,.2f} ${modified_profit - current_profit:>12,.2f}")
    print(f"{'Productos/año':<30} {current_products:>15,.0f} {modified_products:>15,.0f} {modified_products - current_products:>12,.0f}")
    
    # Cálculo de porcentajes
    energy_savings_pct = ((current_energy_cost - modified_energy_cost) / current_energy_cost) * 100
    revenue_reduction_pct = ((current_revenue - modified_revenue) / current_revenue) * 100
    profit_change_pct = ((modified_profit - current_profit) / abs(current_profit)) * 100 if current_profit != 0 else 0
    
    print(f"\n{'Cambios Porcentuales:'}")
    print(f"- Ahorro en energía: {energy_savings_pct:.1f}%")
    print(f"- Reducción en ingresos: {revenue_reduction_pct:.1f}%")
    print(f"- Cambio en utilidad: {profit_change_pct:+.1f}%")
    
    # CONCLUSIÓN
    print("\n" + "="*80)
    print("CONCLUSIÓN")
    print("="*80)
    
    if modified_profit > current_profit:
        conclusion = "✅ SÍ ES RENTABLE - El escenario modificado genera mayor utilidad"
        recommendation = "Se recomienda implementar el cambio"
    elif modified_profit > 0:
        conclusion = "⚠️  PARCIALMENTE RENTABLE - Menor utilidad pero aún positiva"
        recommendation = "Evaluar otros factores antes de decidir"
    else:
        conclusion = "❌ NO ES RENTABLE - El escenario modificado genera pérdidas"
        recommendation = "No se recomienda el cambio"
    
    print(f"\n{conclusion}")
    print(f"\nRecomendación: {recommendation}")
    
    # ROI Analysis
    print(f"\nAnálisis de ROI:")
    current_roi = (current_profit / current_energy_cost) * 100 if current_energy_cost > 0 else 0
    modified_roi = (modified_profit / modified_energy_cost) * 100 if modified_energy_cost > 0 else 0
    
    print(f"- ROI Actual: {current_roi:.1f}%")
    print(f"- ROI Modificado: {modified_roi:.1f}%")
    print(f"- Diferencia ROI: {modified_roi - current_roi:+.1f} puntos porcentuales")
    
    return {
        'escenario_actual': {
            'costo_energia': current_energy_cost,
            'ingresos': current_revenue,
            'utilidad': current_profit,
            'productos': current_products,
            'roi': current_roi
        },
        'escenario_modificado': {
            'costo_energia': modified_energy_cost,
            'ingresos': modified_revenue,
            'utilidad': modified_profit,
            'productos': modified_products,
            'roi': modified_roi
        },
        'es_rentable': modified_profit > current_profit,
        'conclusion': conclusion
    }

# Ejecutar análisis
file_path = r"Modela1Fixeddata.xlsx"
df_list: List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

# Realizar análisis de rentabilidad
resultado_analisis = profitability_analysis(df_list)