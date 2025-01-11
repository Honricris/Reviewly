from app import create_app


# Crear la aplicación
app = create_app()

@app.route('/')
def home():
    return "Bienvenido al servidor de Reviewly"

if __name__ == '__main__':
    app.run(debug=True)
