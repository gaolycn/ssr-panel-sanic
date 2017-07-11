from ssr_panel import app


if __name__ == '__main__':
    app.run(host=app.config.HOST, port=app.config.PORT, workers=app.config.WORKERS, debug=app.config.DEBUG)
