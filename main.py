from src.api_client import APIClient


def main():
    """
    Entry point for the application.
    - Initializes the API client.
    - Fetches all logbook data from the Concept2 API.
    """
    # Initialise API Client
    api_client = APIClient()

    # Request logbook results (handles pagination and token management)
    api_client.fetch_logbook_data_all()


if __name__ == "__main__":
    # Run the application
    main()
