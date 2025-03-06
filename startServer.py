import uvicorn


def start_uvicorn():
    """
    Démarre le serveur Uvicorn en utilisant directement son API Python.
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_config="log_config.yaml",
        reload_dirs=["/app"],
        reload_excludes=["*.log", "*.log"],
    )


if __name__ == "__main__":
    start_uvicorn()
