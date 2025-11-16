import streamlit as st
import pandas as pd
import numpy as np
import math
import sympy as sp  # --- CAMBIO: Importamos SymPy ---

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Integración Numérica",
    page_icon="📐",
    layout="wide"
)

# --- Título ---
st.title("📐 Calculadora de Integración Numérica")
st.write("""
Esta aplicación calcula la integral definida de una función usando múltiples
métodos numéricos (Trapecio, Simpson 1/3, 3/8 y Regla de Boole 2/45).
""")

# --- Barra Lateral de Entradas ---
st.sidebar.header("Parámetros de Entrada")

# --- CAMBIO: Actualicé la función de ejemplo para que no use "math." ---
funcion_original = "(3 * exp(x**2) * sin(2*x**2) + 3) / 1"

# Widgets para los datos de entrada
a = st.sidebar.number_input("Límite inferior (a)", value=1.0, format="%.2f")
b = st.sidebar.number_input("Límite superior (b)", value=1.5, format="%.2f")
N = st.sidebar.number_input("Número de intervalos (N)", value=24, min_value=4, step=1) #Cambié a 24 para que N sea multiplo de 2,3 y 4

# --- CAMBIO: Añadí un texto de ayuda (help) ---
funcion_str = st.sidebar.text_area(
    "Función f(x)", 
    value=funcion_original, 
    height=150,
    help="Escribe la función. Usa 'x' como variable. Ejemplo: sin(x**2) + exp(x) / log(x)"
)

# --- Botón para Calcular ---
if st.sidebar.button("Calcular"):

    # --- CAMBIO: Lógica de SymPy para crear la función ---
    x_sym = sp.symbols('x')  # Define 'x' como un símbolo
    f_lambda = None          # Inicializa la función

    try:
        f_expr = sp.sympify(funcion_str) # Traduce el string a expresión de SymPy
        
        # Convierte la expresión de SymPy a una función de Python rápida
        # "math" es el backend para cálculos numéricos
        f_lambda = sp.lambdify(x_sym, f_expr, "math")
        
        st.success(f"Función reconocida:  `f(x) = {f_expr}`")

    except Exception as e:
        # Captura errores de SINTAXIS (ej. "cos(x" o "1 ++ 2")
        st.error(f"Error en la sintaxis de la función: {e}")
        st.stop() # Detiene la ejecución si la función está mal escrita

    # --- CAMBIO: Nueva función 'f(x)' segura ---
    # Esta función "envuelve" a f_lambda para manejar errores
    # de DOMINIO (ej. log(-1) o 1/0) durante el cálculo.
    def f(x):
        try:
            resultado = f_lambda(x)
            # Si el resultado es complejo (ej. sqrt(-1)), trátalo como error/NaN
            if isinstance(resultado, complex):
                return np.nan
            return resultado
        except ZeroDivisionError:
            return np.nan # Retorna 'Not a Number'
        except Exception:
            # Captura cualquier otro error de dominio (ej. log(-1))
            return np.nan

    # --- FIN DE LOS CAMBIOS PRINCIPALES ---

    try:
        # --- CÁLCULO BASE ---
        h = (b - a) / N
        x_vals = [a + i * h for i in range(N + 1)]
        
        f_vals = []
        for x in x_vals:
            fx = f(x)
            # Verificamos si la función falló (dominio, 1/0, etc.)
            if fx is None or np.isnan(fx):
                st.error(f"Error de dominio o división por cero en x = {x:.4f}. No se puede continuar.")
                # Detiene la ejecución si hay un error en la función
                raise ValueError(f"Error en f({x})")
            f_vals.append(fx)

        # (El resto del código de cálculo de integrales es idéntico)
        # ... (listas para guardar resultados) ...
        resultados_it = {}
        resultados_at = {}
        sumatorias_i = {}
        sumatorias_a = {}

        # --- MÉTODO DEL TRAPECIO ---
        coef_trap = [1] + [2] * (N - 1) + [1]
        I_trap = sum(coef_trap[i] * f_vals[i] for i in range(N + 1))
        A_trap = sum(coef_trap[i] * abs(f_vals[i]) for i in range(N + 1))
        
        resultados_it["Trapecio"] = (h / 2) * I_trap
        resultados_at["Trapecio"] = (h / 2) * A_trap
        sumatorias_i["Trapecio"] = I_trap
        sumatorias_a["Trapecio"] = A_trap

        # --- SIMPSON 1/3 ---
        simpson_usable = (N % 2 == 0)
        if simpson_usable:
            coef_simp = [1] + [4 if i % 2 != 0 else 2 for i in range(1, N)] + [1]
            I_simp = sum(coef_simp[i] * f_vals[i] for i in range(N + 1))
            A_simp = sum(coef_simp[i] * abs(f_vals[i]) for i in range(N + 1))
            
            resultados_it["Simpson 1/3"] = (h / 3) * I_simp
            resultados_at["Simpson 1/3"] = (h / 3) * A_simp
            sumatorias_i["Simpson 1/3"] = I_simp
            sumatorias_a["Simpson 1/3"] = A_simp
        else:
            st.warning("Simpson 1/3 no se calculó. 'N' debe ser un número par.")

        # --- SIMPSON 3/8 ---
        rule38_usable = (N % 3 == 0)
        if rule38_usable:
            coef_38 = [1]
            for i in range(1, N):
                coef_38.append(2 if i % 3 == 0 else 3)
            coef_38.append(1)
            
            I_38 = sum(coef_38[i] * f_vals[i] for i in range(N + 1))
            A_38 = sum(coef_38[i] * abs(f_vals[i]) for i in range(N + 1))
            
            resultados_it["Simpson 3/8"] = (3 * h / 8) * I_38
            resultados_at["Simpson 3/8"] = (3 * h / 8) * A_38
            sumatorias_i["Simpson 3/8"] = I_38
            sumatorias_a["Simpson 3/8"] = A_38
        else:
            st.warning("Simpson 3/8 no se calculó. 'N' debe ser múltiplo de 3.")

        # --- REGLA DE BOOLE (2/45) ---
        rule245_usable = (N % 4 == 0)
        if rule245_usable:
            coef_245 = [7]
            patron = [32, 12, 32, 14]
            for i in range(1, N):
                coef_245.append(patron[(i - 1) % 4])
            coef_245.append(7)
            
            I_245 = sum(coef_245[i] * f_vals[i] for i in range(N + 1))
            A_245 = sum(coef_245[i] * abs(f_vals[i]) for i in range(N + 1))
            
            resultados_it["Boole 2/45"] = (2 * h / 45) * I_245
            resultados_at["Boole 2/45"] = (2 * h / 45) * A_245
            sumatorias_i["Boole 2/45"] = I_245
            sumatorias_a["Boole 2/45"] = A_245
        else:
            st.warning("Regla de Boole (2/45) no se calculó. 'N' debe ser múltiplo de 4.")

        # --- CREACIÓN DE TABLAS CON PANDAS ---
        
        st.header("Resultados Finales")
        
        # Tabla de It y At
        df_finales = pd.DataFrame([resultados_it, resultados_at], index=["It (Integral)", "At (Área)"])
        st.dataframe(df_finales.T.style.format("{:.8f}")) # .T transpone la tabla

        st.header("Información de Cálculo")

        # Dividimos la vista en dos columnas
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sumatorias (I y A)")
            df_sumatorias = pd.DataFrame([sumatorias_i, sumatorias_a], index=["Sumatoria I", "Sumatoria A"])
            st.dataframe(df_sumatorias.T.style.format("{:.8f}"))

        with col2:
            st.subheader("Valores de f(x)")
            # Tabla de x vs f(x)
            df_valores = pd.DataFrame({
                "x": x_vals,
                "f(x)": f_vals
            })
            st.dataframe(df_valores.style.format("{:.8f}"), height=300)

    except ValueError as ve: # Captura el error que lanzamos arriba (ej. dominio)
        st.error(str(ve)) 
    except Exception as e:
        # Captura cualquier error que no hayamos previsto
        st.error(f"Ocurrió un error general: {e}")