import pandas as pd
from typing import List, Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

def define_work_schedules():
    """
    Define los diferentes horarios de trabajo
    """
    schedules = {
        'Actual': {
            'nombre': 'Horario Actual (08:00-20:00)',
            'horas_trabajo': [(8, 20)],  # 12 horas continuas
            'total_horas': 12,
            'descripcion': '12 horas continuas sin descanso'
        },
        'Alternativa_A': {
            'nombre': 'Alternativa A',
            'horas_trabajo': [(4, 12), (16, 24)],  # Descansos: 00:00-04:00 y 12:00-16:00
            'total_horas': 16,
            'descripcion': 'Descansos: 00:00-04:00 y 12:00-16:00 (Trabajo: 04:00-12:00 y 16:00-24:00)'
        },
        'Alternativa_B': {
            'nombre': 'Alternativa B', 
            'horas_trabajo': [(0, 8), (12, 16), (20, 24)],  # Descansos: 08:00-12:00 y 16:00-20:00
            'total_horas': 16,
            'descripcion': 'Descansos: 08:00-12:00 y 16:00-20:00 (Trabajo: 00:00-08:00, 12:00-16:00, 20:00-24:00)'
        },
        'Alternativa_C': {
            'nombre': 'Alternativa C',
            'horas_trabajo': [(0, 8), (12, 20)],  # Descansos: 08:00-12:00 y 20:00-24:00
            'total_horas': 16,
            'descripcion': 'Descansos: 08:00-12:00 y 20:00-24:00 (Trabajo: 00:00-08:00 y 12:00-20:00)'
        }
    }
    
    return schedules

def calculate_energy_cost_by_schedule(df_enero, schedule_info, num_robots=25, consumption_per_robot=0.2):
    """
    Calcula el costo energético para un horario específico usando datos de enero
    """
    total_consumption_per_hour = num_robots * consumption_per_robot
    
    # Obtener horas de trabajo del horario
    work_periods = schedule_info['horas_trabajo']
    
    total_cost = 0
    total_hours_worked = 0
    price_details = []
    
    for start_hour, end_hour in work_periods:
        # Extraer precios para este período
        period_prices = df_enero.iloc[start_hour:end_hour]
        
        for day_col in period_prices.columns:
            day_prices = period_prices[day_col].dropna()
            for price in day_prices:
                cost = price * total_consumption_per_hour
                total_cost += cost
                total_hours_worked += 1
                price_details.append(price)
    
    avg_price = np.mean(price_details) if price_details else 0
    min_price = np.min(price_details) if price_details else 0
    max_price = np.max(price_details) if price_details else 0
    
    return {
        'costo_total': total_cost,
        'horas_trabajadas': total_hours_worked,
        'precio_promedio': avg_price,
        'precio_minimo': min_price,
        'precio_maximo': max_price,
        'precios_detalle': price_details
    }

def calculate_revenue_by_schedule(schedule_info, days_in_month=31):
    """
    Calcula los ingresos basados en las horas de trabajo del horario
    """
    # Parámetros de producción
    num_robots = 25
    minutes_per_product = 15  # tiempo promedio por producto
    products_per_robot_per_hour = 60 / minutes_per_product  # 4 productos/hora
    
    # Ganancia promedio por producto (Grupo Impar)
    avg_profit_per_product_gtq = 405
    gtq_to_usd_rate = 7.8
    avg_profit_per_product_usd = avg_profit_per_product_gtq / gtq_to_usd_rate
    
    # Calcular producción
    hours_per_day = schedule_info['total_horas']
    products_per_day = num_robots * hours_per_day * products_per_robot_per_hour
    products_per_month = products_per_day * days_in_month
    
    monthly_revenue = products_per_month * avg_profit_per_product_usd
    
    return {
        'ingresos_mensuales': monthly_revenue,
        'productos_por_dia': products_per_day,
        'productos_por_mes': products_per_month,
        'horas_por_dia': hours_per_day
    }

def analyze_work_schedule_optimization(df_list):
    """
    Análisis completo de optimización de horarios de trabajo
    """
    print("="*100)
    print("ANÁLISIS DE OPTIMIZACIÓN DE HORARIOS DE TRABAJO")
    print("Mes de análisis: ENERO (mes más rentable)")
    print("="*100)
    
    # Usar datos de enero (mes más rentable - índice 0)
    df_enero = df_list[0]
    
    if df_enero.empty:
        print("Error: No hay datos para enero")
        return
    
    # Definir horarios
    schedules = define_work_schedules()
    
    # Análisis para cada horario
    results = {}
    
    print("\\nDETALLE DE HORARIOS PROPUESTOS:")
    print("="*100)
    
    for schedule_key, schedule_info in schedules.items():
        print(f"\\n{schedule_info['nombre']}:")
        print(f"  • {schedule_info['descripcion']}")
        print(f"  • Total horas diarias: {schedule_info['total_horas']} horas")
        
        # Calcular costos energéticos
        energy_analysis = calculate_energy_cost_by_schedule(df_enero, schedule_info)
        
        # Calcular ingresos
        revenue_analysis = calculate_revenue_by_schedule(schedule_info)
        
        # Calcular utilidad
        profit = revenue_analysis['ingresos_mensuales'] - energy_analysis['costo_total']
        
        # Guardar resultados
        results[schedule_key] = {
            'nombre': schedule_info['nombre'],
            'descripcion': schedule_info['descripcion'],
            'total_horas': schedule_info['total_horas'],
            'costo_energia': energy_analysis['costo_total'],
            'ingresos': revenue_analysis['ingresos_mensuales'],
            'utilidad': profit,
            'productos_mes': revenue_analysis['productos_por_mes'],
            'precio_promedio': energy_analysis['precio_promedio'],
            'horas_trabajadas': energy_analysis['horas_trabajadas'],
            'roi': (profit / energy_analysis['costo_total']) * 100 if energy_analysis['costo_total'] > 0 else 0,
            'margen': (profit / revenue_analysis['ingresos_mensuales']) * 100
        }
        
        print(f"  • Costo energético: ${energy_analysis['costo_total']:,.2f} USD")
        print(f"  • Ingresos: ${revenue_analysis['ingresos_mensuales']:,.2f} USD")
        print(f"  • Utilidad: ${profit:,.2f} USD")
        print(f"  • Productos/mes: {revenue_analysis['productos_por_mes']:,.0f}")
    
    # TABLA COMPARATIVA
    print("\\n" + "="*120)
    print("TABLA COMPARATIVA DE HORARIOS")
    print("="*120)
    
    # Crear DataFrame para mejor visualización
    df_comparison = pd.DataFrame(results).T
    
    print(f"{'Horario':<25} {'Horas/día':<10} {'Costos ($)':<15} {'Ingresos ($)':<15} {'Utilidad ($)':<15} {'ROI (%)':<10} {'Margen (%)':<12}")
    print("-" * 120)
    
    for schedule_key, data in results.items():
        print(f"{data['nombre']:<25} {data['total_horas']:<10} ${data['costo_energia']:<14,.0f} "
              f"${data['ingresos']:<14,.0f} ${data['utilidad']:<14,.0f} {data['roi']:<9.0f}% {data['margen']:<11.1f}%")
    
    # IDENTIFICAR MEJOR ALTERNATIVA
    mejor_alternativa = max(results.items(), key=lambda x: x[1]['utilidad'])
    peor_alternativa = min(results.items(), key=lambda x: x[1]['utilidad'])
    
    print("\\n" + "="*120)
    print("ANÁLISIS DE RESULTADOS")
    print("="*120)
    
    print(f"\\n🏆 MEJOR ALTERNATIVA: {mejor_alternativa[1]['nombre']}")
    print(f"   • Utilidad: ${mejor_alternativa[1]['utilidad']:,.2f} USD")
    print(f"   • ROI: {mejor_alternativa[1]['roi']:.0f}%")
    print(f"   • Productos/mes: {mejor_alternativa[1]['productos_mes']:,.0f}")
    print(f"   • {mejor_alternativa[1]['descripcion']}")
    
    print(f"\\n❌ PEOR ALTERNATIVA: {peor_alternativa[1]['nombre']}")
    print(f"   • Utilidad: ${peor_alternativa[1]['utilidad']:,.2f} USD")
    print(f"   • ROI: {peor_alternativa[1]['roi']:.0f}%")
    print(f"   • {peor_alternativa[1]['descripcion']}")
    
    # Comparar con horario actual
    actual_data = results['Actual']
    mejor_data = mejor_alternativa[1]
    
    mejora_utilidad = mejor_data['utilidad'] - actual_data['utilidad']
    mejora_porcentual = (mejora_utilidad / actual_data['utilidad']) * 100
    
    print(f"\\n💰 MEJORA vs HORARIO ACTUAL:")
    print(f"   • Aumento en utilidad: ${mejora_utilidad:,.2f} USD")
    print(f"   • Mejora porcentual: {mejora_porcentual:+.1f}%")
    print(f"   • Aumento en productos: {mejor_data['productos_mes'] - actual_data['productos_mes']:,.0f} productos/mes")
    
    # ANÁLISIS POR HORAS DEL DÍA
    print("\\n" + "="*120)
    print("ANÁLISIS DE PRECIOS POR HORAS DEL DÍA (ENERO)")
    print("="*120)
    
    # Calcular precio promedio por hora del día
    hourly_prices = []
    for hour in range(24):
        hour_data = df_enero.iloc[hour].dropna()
        if len(hour_data) > 0:
            avg_price = hour_data.mean()
            hourly_prices.append(avg_price)
        else:
            hourly_prices.append(0)
    
    print("\\nPrecio promedio por hora (USD/MWh):")
    for i in range(0, 24, 6):
        hours_slice = hourly_prices[i:i+6]
        hour_labels = [f"{h:02d}:00" for h in range(i, min(i+6, 24))]
        print(f"{' | '.join(f'{label}: ${price:.2f}' for label, price in zip(hour_labels, hours_slice))}")
    
    # Identificar horas más baratas y caras
    cheapest_hours = sorted(enumerate(hourly_prices), key=lambda x: x[1])[:5]
    expensive_hours = sorted(enumerate(hourly_prices), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"\\n⬇️  HORAS MÁS BARATAS:")
    for hour, price in cheapest_hours:
        print(f"   • {hour:02d}:00 - ${price:.2f}/MWh")
    
    print(f"\\n⬆️  HORAS MÁS CARAS:")
    for hour, price in expensive_hours:
        print(f"   • {hour:02d}:00 - ${price:.2f}/MWh")
    
    # CREAR GRÁFICAS
    create_schedule_comparison_charts(results, hourly_prices, schedules)
    
    # RECOMENDACIONES
    print("\\n" + "="*120)
    print("RECOMENDACIONES")
    print("="*120)
    
    print(f"\\n1. 🎯 HORARIO ÓPTIMO: {mejor_alternativa[1]['nombre']}")
    print(f"   • Genera ${mejora_utilidad:,.2f} USD adicionales mensuales")
    print(f"   • Incremento del {mejora_porcentual:.1f}% en rentabilidad")
    
    print(f"\\n2. 📊 BENEFICIOS CLAVE:")
    print(f"   • Mayor tiempo de operación (16 vs 12 horas/día)")
    print(f"   • Mejor aprovechamiento de horas con precios favorables")
    print(f"   • Descansos estratégicos para mantenimiento")
    
    print(f"\\n3. ⚡ OPTIMIZACIÓN ENERGÉTICA:")
    print(f"   • Evitar horas pico de precios energéticos")
    print(f"   • Aprovechar horas valle con precios más bajos")
    print(f"   • Balance entre productividad y costos")
    
    return results, mejor_alternativa, hourly_prices

def create_schedule_comparison_charts(results, hourly_prices, schedules):
    """
    Crear gráficas comparativas de horarios
    """
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 12))
    
    # Colores para cada alternativa
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # Gráfica 1: Comparación de utilidades
    ax1 = plt.subplot(2, 3, 1)
    names = [data['nombre'].replace('Alternativa ', 'Alt. ') for data in results.values()]
    profits = [data['utilidad']/1000 for data in results.values()]
    bars = plt.bar(names, profits, color=colors, alpha=0.8, edgecolor='black')
    
    # Destacar la mejor alternativa
    max_idx = profits.index(max(profits))
    bars[max_idx].set_color('#4CAF50')
    
    plt.title('Comparación de Utilidades\\n(Miles USD)', fontsize=14, fontweight='bold')
    plt.xlabel('Horario', fontweight='bold')
    plt.ylabel('Utilidad (Miles USD)', fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Añadir valores en barras
    for bar, profit in zip(bars, profits):
        plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + bar.get_height()*0.01,
                f'{profit:.0f}k', ha='center', va='bottom', fontweight='bold')
    
    # Gráfica 2: ROI Comparison
    ax2 = plt.subplot(2, 3, 2)
    rois = [data['roi'] for data in results.values()]
    bars2 = plt.bar(names, rois, color=colors, alpha=0.8, edgecolor='black')
    
    plt.title('Comparación de ROI\\n(%)', fontsize=14, fontweight='bold')
    plt.xlabel('Horario', fontweight='bold')
    plt.ylabel('ROI (%)', fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 3: Precios por hora del día
    ax3 = plt.subplot(2, 3, 3)
    hours = list(range(24))
    plt.plot(hours, hourly_prices, marker='o', linewidth=2, color='#e74c3c', markersize=4)
    plt.fill_between(hours, hourly_prices, alpha=0.3, color='#e74c3c')
    
    plt.title('Precios de Energía por Hora\\n(Enero 2023)', fontsize=14, fontweight='bold')
    plt.xlabel('Hora del día', fontweight='bold')
    plt.ylabel('Precio (USD/MWh)', fontweight='bold')
    plt.xticks(range(0, 24, 4), [f'{h}:00' for h in range(0, 24, 4)])
    plt.grid(True, alpha=0.3)
    
    # Gráfica 4: Horarios de trabajo visualización
    ax4 = plt.subplot(2, 3, 4)
    
    schedule_names = list(schedules.keys())
    y_positions = range(len(schedule_names))
    
    for i, (schedule_key, schedule_info) in enumerate(schedules.items()):
        for start, end in schedule_info['horas_trabajo']:
            plt.barh(i, end - start, left=start, height=0.6, 
                    color=colors[i], alpha=0.7, edgecolor='black')
    
    plt.yticks(y_positions, [schedules[key]['nombre'].replace('Alternativa ', 'Alt. ') for key in schedule_names])
    plt.xlabel('Hora del día', fontweight='bold')
    plt.title('Horarios de Trabajo\\n(Barras = Horas Activas)', fontsize=14, fontweight='bold')
    plt.xticks(range(0, 25, 4), [f'{h}:00' for h in range(0, 25, 4)])
    plt.grid(True, alpha=0.3, axis='x')
    
    # Gráfica 5: Costos vs Ingresos
    ax5 = plt.subplot(2, 3, 5)
    costos = [data['costo_energia']/1000 for data in results.values()]
    ingresos = [data['ingresos']/1000 for data in results.values()]
    
    x = np.arange(len(names))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, ingresos, width, label='Ingresos', color='#2ecc71', alpha=0.8)
    bars2 = plt.bar(x + width/2, costos, width, label='Costos', color='#e74c3c', alpha=0.8)
    
    plt.title('Ingresos vs Costos\\n(Miles USD)', fontsize=14, fontweight='bold')
    plt.xlabel('Horario', fontweight='bold')
    plt.ylabel('Miles USD', fontweight='bold')
    plt.xticks(x, [name.replace('Alternativa ', 'Alt. ') for name in names], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    # Gráfica 6: Productos producidos
    ax6 = plt.subplot(2, 3, 6)
    productos = [data['productos_mes']/1000 for data in results.values()]
    bars3 = plt.bar(names, productos, color=colors, alpha=0.8, edgecolor='black')
    
    plt.title('Productos Procesados\\n(Miles/mes)', fontsize=14, fontweight='bold')
    plt.xlabel('Horario', fontweight='bold')
    plt.ylabel('Miles de productos', fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('optimizacion_horarios_enero.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\\n📊 Gráficas guardadas como 'optimizacion_horarios_enero.png'")

# Ejecutar análisis
file_path = r"Modela1Fixeddata.xlsx"
df_list: List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

print("Iniciando análisis de optimización de horarios...")
resultados_horarios, mejor_horario, precios_hora = analyze_work_schedule_optimization(df_list)