from src.watsh.svc.backend.server_setup import configure_logging, initialize_sentry, run_server

if __name__ == "__main__":
    # Configure application logging
    configure_logging()
    print("Logging configured successfully.")

    # Initialize Sentry for error tracking, if enabled
    try:
        initialize_sentry()
        print("Sentry initialized successfully.")
    except Exception as e:
        print(f"Error initializing Sentry: {e}")

    # Run the Uvicorn server
    try:
        run_server()
    except Exception as e:
        print(f"Error running the server: {e}")
