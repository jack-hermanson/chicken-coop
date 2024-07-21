import argparse
from main import create_app


def main():
    # Create the Flask app
    app = create_app()

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run the Flask app.")
    parser.add_argument(
        "--port",
        type=int,
        default=5025,
        help="Port number on which the app should run"
    )
    args = parser.parse_args()

    # Run the app with the specified port
    app.run(debug=True, port=args.port)


if __name__ == "__main__":
    main()
