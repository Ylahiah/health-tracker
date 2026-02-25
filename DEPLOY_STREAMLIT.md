# Guía para Desplegar en Streamlit Community Cloud 🎈

Esta es la forma más fácil y rápida de tener tu aplicación en internet con un enlace público.

## Pasos Previos

Asegúrate de tener una cuenta en:
1.  [GitHub](https://github.com/)
2.  [Streamlit Community Cloud](https://share.streamlit.io/) (conecta tu cuenta de GitHub).

---

## 1. Subir el Código a GitHub

Primero, necesitamos subir tu proyecto a un repositorio de GitHub.

1.  **Abre una terminal** en la carpeta de tu proyecto.
2.  Ejecuta estos comandos uno por uno:

    ```bash
    # Inicializa git si no lo has hecho
    git init
    
    # Agrega todos los archivos
    git add .
    
    # Haz el primer commit
    git commit -m "Initial commit: Health Tracker App"
    ```

3.  Ve a [GitHub.com](https://github.com/new) y crea un **Nuevo Repositorio**.
    *   Nombre: `health-tracker` (o el que quieras).
    *   Público o Privado (Privado es mejor si no quieres que vean tu código, pero Público es más fácil de compartir).
    *   **No** inicialices con README, .gitignore ni licencia (ya los tenemos).

4.  Copia los comandos que te da GitHub para "push an existing repository" y pégalos en tu terminal:

    ```bash
    git branch -M main
    git remote add origin https://github.com/TU_USUARIO/health-tracker.git
    git push -u origin main
    ```

---

## 2. Desplegar en Streamlit Cloud

1.  Ve a [share.streamlit.io](https://share.streamlit.io/).
2.  Haz clic en **"New app"**.
3.  Selecciona tu repositorio (`health-tracker`), la rama (`main`) y el archivo principal (`app/main.py`).
4.  Haz clic en **"Deploy!"**.

---

## 3. Configurar los Secretos (MUY IMPORTANTE) 🔐

Tu aplicación fallará al inicio porque **no tiene las credenciales de Google Sheets** en la nube (recuerda que el archivo `secrets.toml` no se sube a GitHub por seguridad).

1.  En tu dashboard de Streamlit Cloud, busca tu app.
2.  Haz clic en los tres puntos (⋮) al lado de tu app -> **Settings**.
3.  Ve a la sección **Secrets**.
4.  Copia el contenido de tu archivo local `.streamlit/secrets.toml` y pégalo en el cuadro de texto.

    Debería verse así:

    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "..."
    # ... resto de tus credenciales ...

    [spreadsheet]
    name = "Health_Tracker_DB"
    ```

5.  Haz clic en **Save**.

¡Listo! Streamlit reiniciará tu app automáticamente y ahora sí podrá conectarse a Google Sheets.

---

## 4. Notas sobre la IA en la Nube

Streamlit Cloud tiene recursos limitados.
*   Si la app se reinicia sola al usar la cámara, puede ser por falta de memoria.
*   En `packages.txt` (si fuera necesario), se agregan dependencias de sistema. Para este proyecto, el `requirements.txt` ya incluye `opencv-python-headless` que suele funcionar bien.
