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
from scipy.special import comb  # Más estable que math.comb (admite floats grandes)

app = FastAPI(
    title="📊 Calculadora de Distribución de Poisson",
    description="API + Interfaz Web para calcular probabilidades de Poisson y visualizar gráficos.",
    version="1.0.0"
)

# Configurar plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelo para la API (JSON)
class PoissonRequest(BaseModel):
    lam: float
    x: int

# Modelo para respuesta de la API
class PoissonResponse(BaseModel):
    probability: float
    formula: str
    lambda_value: float
    x_value: int
    plot_url: Optional[str] = None

def poisson_pmf(x: int, lam: float) -> float:
    """Calcula P(X = x) para distribución de Poisson"""
    if x < 0 or lam <= 0:
        return 0.0
    return (exp(-lam) * (lam ** x)) / factorial(x)

def generate_poisson_plot_base64(lam: float, max_x: int = 15) -> str:
    """Genera gráfico de Poisson y lo devuelve como string base64"""
    x_vals = np.arange(0, max_x + 1)
    y_vals = [poisson_pmf(x, lam) for x in x_vals]

    plt.figure(figsize=(10, 5))
    plt.bar(x_vals, y_vals, color='steelblue', edgecolor='black')
    plt.title(f'Distribución de Poisson (λ = {lam})')
    plt.xlabel('x (número de eventos)')
    plt.ylabel('P(X = x)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(x_vals)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# 🌐 Ruta principal: sirve la interfaz HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 📊 Ruta POST desde formulario HTML
@app.post("/", response_class=HTMLResponse)
async def calculate_from_form(
    request: Request,
    lam: float = Form(..., gt=0),
    x: int = Form(..., ge=0)
):
    try:
        prob = poisson_pmf(x, lam)
        formula = f"P(X = {x}) = e^(-{lam}) * {lam}^{x} / {x}!"
        plot_url = generate_poisson_plot_base64(lam, max_x=int(lam*3) if lam*3 > 15 else 15)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": f"P(X = {x}) = {prob:.6f}",
            "formula": formula,
            "plot_url": plot_url,
            "lam": lam,
            "x": x
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": f"Error: {str(e)}",
            "lam": lam,
            "x": x
        })

# 🧮 Ruta API (JSON) - para consumo programático
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


# === HIPERGEOMÉTRICA ===

def hypergeometric_pmf(x: int, N: int, K: int, n: int) -> float:
    """
    Calcula P(X = x) para distribución hipergeométrica.
    """
    if x < max(0, n + K - N) or x > min(n, K):
        return 0.0
    numerator = comb(K, x) * comb(N - K, n - x)
    denominator = comb(N, n)
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)

def generate_hypergeometric_plot_base64(N: int, K: int, n: int) -> str:
    """
    Genera gráfico de la distribución hipergeométrica.
    """
    min_x = max(0, n + K - N)
    max_x = min(n, K)
    x_vals = list(range(min_x, max_x + 1))
    y_vals = [hypergeometric_pmf(x, N, K, n) for x in x_vals]

    plt.figure(figsize=(10, 5))
    plt.bar(x_vals, y_vals, color='indianred', edgecolor='black')
    plt.title(f'Distribución Hipergeométrica (N={N}, K={K}, n={n})')
    plt.xlabel('x (número de éxitos en muestra)')
    plt.ylabel('P(X = x)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(x_vals)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# Modelos Pydantic para la API
class HypergeometricRequest(BaseModel):
    N: int
    K: int
    n: int
    x: int

class HypergeometricResponse(BaseModel):
    probability: float
    formula: str
    N: int
    K: int
    n: int
    x: int
    plot_url: Optional[str] = None

# 🧮 Ruta API para Hipergeométrica
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

# 🌐 Ruta HTML para formulario Hipergeométrica
@app.get("/hyper", response_class=HTMLResponse)
async def hyper_form(request: Request):
    return templates.TemplateResponse("hyper.html", {"request": request})

@app.post("/hyper", response_class=HTMLResponse)
async def calculate_hyper_from_form(
    request: Request,
    N: int = Form(..., gt=0),
    K: int = Form(..., ge=0),
    n: int = Form(..., gt=0),
    x: int = Form(..., ge=0)
):
    try:
        if K > N or n > N or x > n or x > K:
            raise ValueError("Valores inconsistentes: revisa que K ≤ N, n ≤ N, x ≤ n y x ≤ K.")

        prob = hypergeometric_pmf(x, N, K, n)
        formula = f"P(X = {x}) = C({K},{x}) * C({N - K},{n - x}) / C({N},{n})"
        plot_url = generate_hypergeometric_plot_base64(N, K, n)

        return templates.TemplateResponse("hyper.html", {
            "request": request,
            "result": f"P(X = {x}) = {prob:.6f}",
            "formula": formula,
            "plot_url": plot_url,
            "N": N, "K": K, "n": n, "x": x
        })
    except Exception as e:
        return templates.TemplateResponse("hyper.html", {
            "request": request,
            "result": f"Error: {str(e)}",
            "N": N, "K": K, "n": n, "x": x
        })