# Guía de Configuración de GitHub 🐙

Sigue estos pasos para subir tu código a GitHub.

## 1. Inicializar Repositorio

Abre la terminal en la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Initial commit: Health Tracker App structure and features"
```

## 2. Crear Repositorio en GitHub

1.  Ve a [github.com/new](https://github.com/new).
2.  Crea un repositorio llamado `health-tracker` (o como prefieras).
3.  No inicialices con README ni .gitignore (ya los tenemos).

## 3. Conectar y Subir

Copia los comandos que te da GitHub, parecidos a estos:

```bash
git branch -M main
git remote add origin https://github.com/TU_USUARIO/health-tracker.git
git push -u origin main
```

## 4. Importante sobre Seguridad 🔒

El archivo `.gitignore` ya está configurado para **ignorar**:
- `.streamlit/secrets.toml`
- `service_account.json`
- `.env`

**NUNCA subas tus credenciales a GitHub.** Si lo haces, revócalas inmediatamente en la consola de Google Cloud.

## 5. Colaboración

Si haces cambios en el futuro:

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```
