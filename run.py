import os
from main import create_app

app = create_app()

if __name__ == "__main__":
    x = os.environ.get("PORT")
    port = int(os.environ.get("PORT", 5025))
    app.run(debug=True, port=port)
