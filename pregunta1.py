import pandas as pd
from typing import List
import numpy as np

def read_excel_sheets_to_dataframes(file_path):
    """
    Read Excel file with sheets named 1-12 and return list of DataFrames
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        list: List of DataFrames, one for each sheet
    """
    dataframes = []
    
    # Read each sheet by name (1 through 12)
    for sheet_num in range(1, 13):
        try:
            df = pd.read_excel(file_path, sheet_name=str(sheet_num))
            dataframes.append(df)
            print(f"Successfully read sheet '{sheet_num}' with shape {df.shape}")
        except Exception as e:
            print(f"Error reading sheet '{sheet_num}': {e}")
            # Append empty DataFrame if sheet doesn't exist or has error
            dataframes.append(pd.DataFrame())
    
    return dataframes

def calculate_energy_cost(df_list: List[pd.DataFrame]):
    """
    Calcula el costo total del consumo energético para el año 2023
    
    Args:
        df_list: Lista de DataFrames con precios de energía por mes
    
    Returns:
        dict: Diccionario con costos detallados
    """
    # Parámetros del sistema
    num_robots = 25
    consumption_per_robot = 0.2  # MWh por hora
    total_consumption_per_hour = num_robots * consumption_per_robot  # 5 MWh por hora
    
    # Horas de operación (8:00 a 20:00 = filas 8 a 19, índices 8-19)
    working_hours_start = 8  # 8:00 AM
    working_hours_end = 20   # 8:00 PM (fila 19 = 19:00-19:59)
    
    print(f"Parámetros del sistema:")
    print(f"- Número de robots: {num_robots}")
    print(f"- Consumo por robot: {consumption_per_robot} MWh/hora")
    print(f"- Consumo total por hora: {total_consumption_per_hour} MWh/hora")
    print(f"- Horario de operación: {working_hours_start}:00 - {working_hours_end}:00")
    print(f"- Horas de trabajo por día: {working_hours_end - working_hours_start}")
    print()
    
    monthly_costs = []
    monthly_details = []
    
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    for month_idx, df in enumerate(df_list):
        if df.empty:
            print(f"Mes {month_idx + 1} ({months[month_idx]}): Sin datos")
            monthly_costs.append(0)
            continue
            
        month_name = months[month_idx]
        print(f"Procesando {month_name} (Mes {month_idx + 1})")
        
        # Extraer precios del horario laboral (filas 8-19)
        working_hours_prices = df.iloc[working_hours_start:working_hours_end]
        
        # Calcular costo por cada hora de cada día
        daily_costs = []
        total_hours_worked = 0
        
        for day in working_hours_prices.columns:
            day_prices = working_hours_prices[day]
            # Filtrar valores NaN
            valid_prices = day_prices.dropna()
            
            if len(valid_prices) > 0:
                # Costo por día = suma de (precio_hora * consumo_por_hora) para todas las horas laborales
                daily_cost = sum(price * total_consumption_per_hour for price in valid_prices)
                daily_costs.append(daily_cost)
                total_hours_worked += len(valid_prices)
        
        month_cost = sum(daily_costs)
        monthly_costs.append(month_cost)
        
        # Estadísticas del mes
        all_working_prices = []
        for day in working_hours_prices.columns:
            day_prices = working_hours_prices[day].dropna()
            all_working_prices.extend(day_prices)
        
        if all_working_prices:
            avg_price = np.mean(all_working_prices)
            min_price = np.min(all_working_prices)
            max_price = np.max(all_working_prices)
            
            monthly_details.append({
                'mes': month_name,
                'costo_total': month_cost,
                'horas_trabajadas': total_hours_worked,
                'precio_promedio': avg_price,
                'precio_minimo': min_price,
                'precio_maximo': max_price,
                'dias_con_datos': len(daily_costs)
            })
            
            print(f"  - Costo total: ${month_cost:,.2f} USD")
            print(f"  - Horas trabajadas: {total_hours_worked}")
            print(f"  - Precio promedio: ${avg_price:.2f} USD/MWh")
            print(f"  - Días con datos: {len(daily_costs)}")
        else:
            print(f"  - Sin datos válidos para {month_name}")
        
        print()
    
    # Costo total anual
    total_annual_cost = sum(monthly_costs)
    
    # Resumen
    print("="*60)
    print("RESUMEN ANUAL - COSTO CONSUMO ENERGÉTICO 2023")
    print("="*60)
    print(f"Costo total anual: ${total_annual_cost:,.2f} USD")
    print(f"Costo promedio mensual: ${total_annual_cost/12:,.2f} USD")
    
    # Mes más caro y más barato
    if monthly_costs:
        max_month_idx = monthly_costs.index(max(monthly_costs))
        min_month_idx = monthly_costs.index(min(monthly_costs))
        
        print(f"Mes más caro: {months[max_month_idx]} (${monthly_costs[max_month_idx]:,.2f} USD)")
        print(f"Mes más barato: {months[min_month_idx]} (${monthly_costs[min_month_idx]:,.2f} USD)")
    
    print()
    print("Desglose mensual:")
    for i, (month, cost) in enumerate(zip(months, monthly_costs)):
        percentage = (cost / total_annual_cost * 100) if total_annual_cost > 0 else 0
        print(f"{month:>12}: ${cost:>10,.2f} USD ({percentage:>5.1f}%)")
    
    return {
        'costo_total_anual': total_annual_cost,
        'costos_mensuales': monthly_costs,
        'detalles_mensuales': monthly_details,
        'parametros': {
            'num_robots': num_robots,
            'consumo_por_robot': consumption_per_robot,
            'consumo_total_por_hora': total_consumption_per_hour,
            'horas_operacion_diaria': working_hours_end - working_hours_start
        }
    }

# Uso del código
file_path = r"Modela1Fixeddata.xlsx"
df_list: List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

# Calcular el costo del consumo energético
resultado = calculate_energy_cost(df_list)

# Mostrar resultado principal
print("\n" + "="*80)
print("RESPUESTA A LA PREGUNTA:")
print("="*80)
print(f"El costo actual del consumo energético para los 25 robots que consumen")
print(f"0.2 MWh cada uno durante el horario laboral (8:00-20:00) es:")
print(f"\n${resultado['costo_total_anual']:,.2f} USD anuales")
print("="*80)