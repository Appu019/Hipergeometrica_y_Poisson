from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from math import exp, factorial
from pydantic import BaseModel
from typing import Optional
from scipy.special import comb  # Función combinatoria más estable que math.comb

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title="📊 Calculadora de Distribución de Poisson",
    description="API + Interfaz Web para calcular probabilidades de Poisson y visualizar gráficos.",
    version="1.0.0"
)

# Configurar el directorio de plantillas HTML
templates = Jinja2Templates(directory="templates")

# Montar archivos estáticos (CSS, JS, imágenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelo de entrada para la API de Poisson
class PoissonRequest(BaseModel):
    lam: float  # Parámetro lambda (tasa promedio de eventos)
    x: int      # Número de eventos

# Modelo de salida para la API de Poisson
class PoissonResponse(BaseModel):
    probability: float  # Probabilidad calculada
    formula: str        # Fórmula utilizada
    lambda_value: float # Valor de lambda
    x_value: int        # Valor de x
    plot_url: Optional[str] = None  # URL del gráfico en formato base64

# Función para calcular la probabilidad de Poisson (P(X = x))
def poisson_pmf(x: int, lam: float) -> float:
    """Calcula P(X = x) para distribución de Poisson."""
    if x < 0 or lam <= 0:  # Validar que los valores sean válidos
        return 0.0
    return (exp(-lam) * (lam ** x)) / factorial(x)  # Fórmula de Poisson

# Función para generar un gráfico de Poisson en formato base64
def generate_poisson_plot_base64(lam: float, max_x: int = 15) -> str:
    """Genera gráfico de Poisson y lo devuelve como string base64."""
    x_vals = np.arange(0, max_x + 1)  # Valores de x (0 a max_x)
    y_vals = [poisson_pmf(x, lam) for x in x_vals]  # Calcular P(X = x) para cada x

    # Crear el gráfico
    plt.figure(figsize=(10, 5))
    plt.bar(x_vals, y_vals, color='steelblue', edgecolor='black')
    plt.title(f'Distribución de Poisson (λ = {lam})')
    plt.xlabel('x (número de eventos)')
    plt.ylabel('P(X = x)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(x_vals)

    # Guardar el gráfico en un buffer y convertirlo a base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# Ruta principal: sirve la interfaz HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Renderiza la página principal con el formulario."""
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta POST para calcular Poisson desde el formulario HTML
@app.post("/", response_class=HTMLResponse)
async def calculate_from_form(
    request: Request,
    lam: float = Form(..., gt=0),  # Lambda debe ser mayor que 0
    x: int = Form(..., ge=0)      # x debe ser mayor o igual a 0
):
    try:
        # Calcular la probabilidad y generar el gráfico
        prob = poisson_pmf(x, lam)
        formula = f"P(X = {x}) = e^(-{lam}) * {lam}^{x} / {x}!"
        plot_url = generate_poisson_plot_base64(lam, max_x=int(lam*3) if lam*3 > 15 else 15)

        # Renderizar la respuesta en la página HTML
        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": f"P(X = {x}) = {prob:.6f}",
            "formula": formula,
            "plot_url": plot_url,
            "lam": lam,
            "x": x
        })
    except Exception as e:
        # Manejar errores y mostrarlos en la página
        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": f"Error: {str(e)}",
            "lam": lam,
            "x": x
        })

# Ruta API para calcular Poisson (JSON)
@app.post("/api/poisson", response_model=PoissonResponse)
async def calculate_poisson_api(request: PoissonRequest):
    """
    Calcula la probabilidad P(X = x) para una distribución de Poisson.
    Devuelve probabilidad, fórmula y gráfico en base64.
    """
    prob = poisson_pmf(request.x, request.lam)
    formula = f"P(X = {request.x}) = e^(-{request.lam}) * {request.lam}^{request.x} / {request.x}!"
    plot_url = generate_poisson_plot_base64(request.lam, max_x=int(request.lam*3) if request.lam*3 > 15 else 15)

    return PoissonResponse(
        probability=prob,
        formula=formula,
        lambda_value=request.lam,
        x_value=request.x,
        plot_url=plot_url
    )

# === Funciones y rutas para la distribución hipergeométrica ===

# Función para calcular la probabilidad de la distribución hipergeométrica
def hypergeometric_pmf(x: int, N: int, K: int, n: int) -> float:
    """
    Calcula P(X = x) para distribución hipergeométrica.
    """
    if x < max(0, n + K - N) or x > min(n, K):  # Validar límites de x
        return 0.0
    numerator = comb(K, x) * comb(N - K, n - x)  # Numerador de la fórmula
    denominator = comb(N, n)  # Denominador de la fórmula
    if denominator == 0:  # Evitar división por cero
        return 0.0
    return float(numerator / denominator)

# Función para generar un gráfico de la distribución hipergeométrica
def generate_hypergeometric_plot_base64(N: int, K: int, n: int) -> str:
    """
    Genera gráfico de la distribución hipergeométrica.
    """
    min_x = max(0, n + K - N)  # Valor mínimo de x
    max_x = min(n, K)          # Valor máximo de x
    x_vals = list(range(min_x, max_x + 1))  # Valores de x
    y_vals = [hypergeometric_pmf(x, N, K, n) for x in x_vals]  # Calcular P(X = x)

    # Crear el gráfico
    plt.figure(figsize=(10, 5))
    plt.bar(x_vals, y_vals, color='indianred', edgecolor='black')
    plt.title(f'Distribución Hipergeométrica (N={N}, K={K}, n={n})')
    plt.xlabel('x (número de éxitos en muestra)')
    plt.ylabel('P(X = x)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(x_vals)

    # Guardar el gráfico en un buffer y convertirlo a base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# Modelos de entrada y salida para la API de hipergeométrica
class HypergeometricRequest(BaseModel):
    N: int  # Tamaño de la población
    K: int  # Número de éxitos en la población
    n: int  # Tamaño de la muestra
    x: int  # Número de éxitos en la muestra

class HypergeometricResponse(BaseModel):
    probability: float  # Probabilidad calculada
    formula: str        # Fórmula utilizada
    N: int              # Tamaño de la población
    K: int              # Número de éxitos en la población
    n: int              # Tamaño de la muestra
    x: int              # Número de éxitos en la muestra
    plot_url: Optional[str] = None  # URL del gráfico en formato base64

# Ruta API para calcular hipergeométrica (JSON)
@app.post("/api/hypergeometric", response_model=HypergeometricResponse)
async def calculate_hypergeometric_api(request: HypergeometricRequest):
    """
    Calcula P(X = x) para distribución hipergeométrica.
    """
    prob = hypergeometric_pmf(request.x, request.N, request.K, request.n)
    formula = f"P(X = {request.x}) = C({request.K},{request.x}) * C({request.N - request.K},{request.n - request.x}) / C({request.N},{request.n})"
    plot_url = generate_hypergeometric_plot_base64(request.N, request.K, request.n)

    return HypergeometricResponse(
        probability=prob,
        formula=formula,
        N=request.N,
        K=request.K,
        n=request.n,
        x=request.x,
        plot_url=plot_url
    )

# Ruta HTML para el formulario de hipergeométrica
@app.get("/hyper", response_class=HTMLResponse)
async def hyper_form(request: Request):
    """Renderiza la página del formulario para hipergeométrica."""
    return templates.TemplateResponse("hyper.html", {"request": request})

# Ruta POST para calcular hipergeométrica desde el formulario HTML
@app.post("/hyper", response_class=HTMLResponse)
async def calculate_hyper_from_form(
    request: Request,
    N: int = Form(..., gt=0),  # N debe ser mayor que 0
    K: int = Form(..., ge=0),  # K debe ser mayor o igual a 0
    n: int = Form(..., gt=0),  # n debe ser mayor que 0
    x: int = Form(..., ge=0)   # x debe ser mayor o igual a 0
):
    try:
        # Validar que los valores sean consistentes
        if K > N or n > N or x > n or x > K:
            raise ValueError("Valores inconsistentes: revisa que K ≤ N, n ≤ N, x ≤ n y x ≤ K.")

        # Calcular la probabilidad y generar el gráfico
        prob = hypergeometric_pmf(x, N, K, n)
        formula = f"P(X = {x}) = C({K},{x}) * C({N - K},{n - x}) / C({N},{n})"
        plot_url = generate_hypergeometric_plot_base64(N, K, n)

        # Renderizar la respuesta en la página HTML
        return templates.TemplateResponse("hyper.html", {
            "request": request,
            "result": f"P(X = {x}) = {prob:.6f}",
            "formula": formula,
            "plot_url": plot_url,
            "N": N, "K": K, "n": n, "x": x
        })
    except Exception as e:
        # Manejar errores y mostrarlos en la página
        return templates.TemplateResponse("hyper.html", {
            "request": request,
            "result": f"Error: {str(e)}",
            "N": N, "K": K, "n": n, "x": x
        })
