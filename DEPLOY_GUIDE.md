# 🚀 Guía de Despliegue Gratuito en la Nube y Protocolo de Ciberseguridad

Esta guía detalla paso a paso cómo subir tu aplicación **NBAEdge AI** a GitHub y desplegarla en internet **100% gratis** (sin pagar servidores ni dominios), garantizando que **nadie tenga acceso a tus API Keys**.

---

## 🛡️ 1. Medidas de Ciberseguridad Implementadas (Grado Empresarial)

Tu sistema ha sido blindado siguiendo las recomendaciones de seguridad **OWASP Top 10**:

1. **Aislamiento Absoluto de Secretos (`Zero-Trust`)**:
   - Tu clave de *The Odds API* está almacenada exclusivamente en el archivo local `.env`.
   - El archivo `.gitignore` y `.dockerignore` tienen reglas estrictas que impiden que `.env`, `.env.*`, claves privadas o credenciales se suban a GitHub.
   - La API (`/api/settings`) enmascara automáticamente tu clave (`5b46...ad88`), evitando que se filtre en respuestas JSON.
   - El frontend de React **nunca** se comunica directamente con The Odds API; todas las peticiones pasan por el backend en Python.

2. **Cabeceras de Seguridad Avanzadas (Defensa en Profundidad)**:
   - `Content-Security-Policy (CSP)`: Bloquea ejecución de scripts maliciosos (XSS) y llamadas a dominios no autorizados.
   - `X-Frame-Options: DENY`: Evita ataques de *Clickjacking* (nadie puede incrustar tu web en un iframe oculto).
   - `X-Content-Type-Options: nosniff`: Impide que el navegador interprete archivos maliciosos como scripts.
   - `Strict-Transport-Security (HSTS)`: Fuerza conexiones cifradas HTTPS durante 1 año.
   - `Referrer-Policy: strict-origin-when-cross-origin`: Impide que rutas internas o parámetros se filtren en cabeceras de navegación.

3. **Protección Anti-DDoS y Rate Limiting (Sliding Window)**:
   - Middleware de limitación de tasa por IP:
     - Endpoints de lectura (analíticas y cuotas): máx. 120 peticiones por minuto.
     - Endpoints de escritura (ajustes de líneas y bankroll): máx. 25 peticiones por minuto.
   - Si un usuario malintencionado intenta saturar la web, recibe automáticamente un error `429 Too Many Requests`.

4. **Validación Estricta de Entradas con Pydantic**:
   - Se valida el rango numérico y tipo de dato de cada línea y ajuste para impedir inyecciones SQL o desbordamientos.

5. **Caché Inteligente de Cuota (15 minutos)**:
   - Cada llamada a *The Odds API* queda en caché durante 15 minutos en memoria y disco. Esto garantiza que las 500 peticiones mensuales gratuitas no se agoten por refrescar la página.

---

## 🌐 2. Cómo Subir el Proyecto a GitHub de Forma 100% Segura

### Paso 1: Comprobar que `.env` NO se va a subir
Ejecuta en tu terminal para estar 100% seguro:
```bash
git status -s
```
Verás que `.env` **no aparece en la lista** (está completamente ignorado por Git).

### Paso 2: Crear tu repositorio en GitHub
1. Entra en [github.com](https://github.com) e inicia sesión.
2. Haz clic en el botón verde **"New repository"**.
3. Ponle un nombre, por ejemplo: `nba-edge-predictor`.
4. Elige si quieres que sea **Público** o **Privado** (incluso si es público, tus API Keys NO se subirán porque están en `.env`).
5. **NO** marques "Add a README" ni "Add .gitignore" (ya los tenemos creados).
6. Haz clic en **"Create repository"**.

### Paso 3: Subir tu código a GitHub
Copia la URL de tu nuevo repositorio de GitHub y ejecuta estos 3 comandos en tu terminal:

```bash
git add .
git commit -m "feat: hardened production release with security headers and docker deployment"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/nba-edge-predictor.git
git push -u origin main
```

---

## ☁️ 3. Despliegue Gratuito en Render.com (Recomendado)

[Render.com](https://render.com) ofrece un **Free Tier permanente** para aplicaciones web que incluye:
- Servidor web gratuito ($0 / mes).
- Certificado SSL automático (HTTPS seguro `https://tu-app.onrender.com`).
- Despliegue automático con cada `git push`.
- Servidor ubicado en Frankfurt (Alemania), ideal para conexiones rápidas desde España (Bet365 / Winamax).

### Pasos para desplegar en Render:

1. Ve a [https://render.com](https://render.com) y regístrate gratis con tu cuenta de GitHub.
2. En el panel principal, haz clic en **New +** y selecciona **Blueprint** (o **Web Service**).
3. Conecta tu repositorio de GitHub `nba-edge-predictor`.
4. Render leerá automáticamente el archivo `render.yaml` incluido en el proyecto.
5. **Configuración de Secretos en Render (Seguro)**:
   - En la sección **Environment Variables**, añade:
     - `ODDS_API_KEY`: `tu_clave_de_the_odds_api`
     - `ENVIRONMENT`: `production`
6. Haz clic en **Apply** / **Create Web Service**.
7. En unos 2-3 minutos, Render compilará el frontend en React, instalará el backend en Python y te dará tu enlace público gratuito (ejemplo: `https://nba-edge-predictor.onrender.com`).

---

## 🔄 4. Alternativas Gratuitas Adicionales

Si prefieres otra plataforma alternativa:
- **Railway.app**: Ofrece $5 de crédito mensual gratuito y soporta Docker de forma nativa.
- **Fly.io**: Permite desplegar hasta 3 máquinas virtuales gratis con `fly launch`.
- **Hugging Face Spaces**: Permite alojar aplicaciones Docker de forma 100% gratuita indefinidamente.

---

## ✅ 5. Resumen de Seguridad

| Vulnerabilidad / Riesgo | Solución Implementada | Estado |
|---|---|---|
| **Fuga de API Keys** | `.gitignore` estricto + variables de entorno + enmascaramiento UI (`5b46...ad88`) | 🔒 Blindado |
| **Inyección XSS** | React sanitization + Content-Security-Policy (CSP) | 🔒 Blindado |
| **Clickjacking** | `X-Frame-Options: DENY` | 🔒 Blindado |
| **Ataques DoS / Fuerza Bruta** | Sliding Window Rate Limiter (Starlette Middleware) | 🔒 Blindado |
| **Inyección Maliciosa de Datos** | Modelos Pydantic v2 con validación de tipo y rango | 🔒 Blindado |
| **Agotamiento de Cuota de Odds** | Caché inteligente de 15 minutos en memoria y disco | 🔒 Optimizado |

