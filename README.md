
📊 PROYECTO: CALCULADORA DE DISTRIBUCIONES ESTADÍSTICAS
              (Poisson + Hipergeométrica)


Autor: Cristopher Coaquira
Tecnologías: Python, FastAPI, Matplotlib, Jinja2, Uvicorn
Última actualización: Mayo 2025

------------------------------------------------------------
📌 DESCRIPCIÓN
------------------------------------------------------------

Esta aplicación web permite calcular probabilidades y visualizar gráficos de dos distribuciones discretas clave:

1. 📘 Distribución de Poisson — para eventos independientes en intervalo fijo.
2. 🎯 Distribución Hipergeométrica — para muestreos sin reemplazo en población finita.

Incluye:
✅ Interfaz web interactiva (HTML + CSS)
✅ API REST con validación automática (Pydantic)
✅ Documentación automática (Swagger UI)
✅ Gráficos dinámicos en base64
✅ Código modular y fácil de extender

Ideal para educación, consulta estadística o como base para proyectos de ciencia de datos.

------------------------------------------------------------
⚙️ REQUISITOS
------------------------------------------------------------

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

------------------------------------------------------------
📦 INSTALACIÓN
------------------------------------------------------------

1. Clona o descarga este proyecto en tu computadora.

2. Abre una terminal en la carpeta del proyecto.

3. Instala las dependencias:

   pip install -r requirements.txt

------------------------------------------------------------
🚀 EJECUCIÓN
------------------------------------------------------------

En la terminal, ejecuta:

   uvicorn main:app --reload

Luego abre tu navegador en:

   👉 Interfaz Poisson:     http://127.0.0.1:8000
   👉 Interfaz Hipergeométrica: http://127.0.0.1:8000/hyper
   👉 Documentación API:    http://127.0.0.1:8000/docs

------------------------------------------------------------
🧪 EJEMPLOS DE USO
------------------------------------------------------------

▶️ POISSON:
   λ = 3 (promedio de eventos por hora)
   x = 5 (¿cuál es la probabilidad de 5 eventos?)
   → Resultado: P(X=5) ≈ 0.1008

▶️ HIPERGEOMÉTRICA:
   N = 20 (población total)
   K = 5 (éxitos en población)
   n = 4 (tamaño de muestra)
   x = 2 (éxitos deseados en muestra)
   → Resultado: P(X=2) ≈ 0.2167

------------------------------------------------------------
📁 ESTRUCTURA DEL PROYECTO
------------------------------------------------------------

poisson_fastapi/
│
├── main.py                 ← App principal (FastAPI)
├── requirements.txt        ← Dependencias
├── README.txt              ← Este archivo
│
├── static/
│   └── style.css           ← Estilos CSS (opcional)
│
└── templates/
    ├── index.html          ← Interfaz Poisson
    └── hyper.html          ← Interfaz Hipergeométrica

------------------------------------------------------------
🔧 ERRORES COMUNES Y SOLUCIONES
------------------------------------------------------------

❌ ERROR: "Failed to load resource: 404" con cadena base64 larga
→ CAUSA: Falta el prefijo "data:" en la etiqueta <img src="...">
→ SOLUCIÓN: Asegúrate de que el src sea:
      src="image/png;base64,{{ plot_url }}"

❌ ERROR: ModuleNotFoundError: No module named 'scipy'
→ SOLUCIÓN: Ejecuta: pip install scipy

❌ ERROR: No se muestra el gráfico
→ SOLUCIÓN: Verifica que matplotlib y numpy estén instalados.
            Reinicia el servidor con --reload.

------------------------------------------------------------
🚀 PRÓXIMOS PASOS / MEJORAS SUGERIDAS
------------------------------------------------------------

- Añadir distribución binomial.
- Comparar gráficos lado a lado.
- Exportar resultados a PDF o Excel.
- Añadir cálculo de probabilidad acumulada.
- Desplegar en la nube (Render, Railway, Vercel).
- Añadir autenticación básica.
- Internacionalización (inglés/español).

------------------------------------------------------------
📬 CONTACTO / SOPORTE
------------------------------------------------------------

¿Encontraste un bug? ¿Quieres sugerir una mejora?
→ Abre un "Issue" en el repositorio o contacta al autor.

------------------------------------------------------------
✅ LICENCIA
------------------------------------------------------------

Proyecto de uso educativo y libre. 
Puedes modificarlo, compartirlo y mejorarlo sin restricciones.


¡Gracias por usar esta herramienta! 
Esperamos que te sea útil en tus estudios o proyectos.
