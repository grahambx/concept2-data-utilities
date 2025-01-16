import os
from src.api_client import APIClient
from src.data_processor import RowingDataProcessor


def main():
    """
    Entry point for the application.
    - Initializes the API client.
    - Fetches all logbook data from the Concept2 API.
    - Process data to convert to csv + xslx (have not unpacked nested lap data)
    - Process data to generate a weekly report and save as csv + xlsx
    """
    # Initialise API Client
    api_client = APIClient()

    # Request logbook results (handles pagination and token management)
    api_client.fetch_logbook_data_all()

    # Complete Data processing
    input_folder = "output"
    output_folder = "output"
    print("\nAttempting to process data...")
    processor = RowingDataProcessor(input_folder, output_folder)
    processor.process()

    # Open Aggregate weekly summary xlsx
    # TODO - below will only work for Windows
    os.startfile(os.path.join(output_folder, 'weekly-report.xlsx'))


if __name__ == "__main__":
    # Run the application
    main()
