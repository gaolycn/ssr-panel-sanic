from ss_panel import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config.PORT, workers=app.config.WORKERS, debug=app.config.DEBUG)
