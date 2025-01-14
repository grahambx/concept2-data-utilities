import requests
import json
from credential_manager import CredentialManager


class APIClient:
    def __init__(self):
        """
        Initializes the API client with:
        - An instance of CredentialManager for authentication.
        - Required API headers for authorization.
        - Pagination variables for fetching results.
        """
        self.cm = CredentialManager()
        self.start_logbook_url = "https://log.concept2.com/api/users/me/results"
        self.headers = {
            "Authorization": f"Bearer {self.cm.tokens['access_token']}",
            "Accept": "application/vnd.c2logbook.v1+json"
        }
        self.page = 1  # Current page number, used for pagination
        self.next_logbook_url = self.start_logbook_url  # URL for the next page to fetch

    def fetch_logbook_data_all(self):
        """
        Fetches all logbook data across multiple pages:
        - Iterates through pages using `get_all_pages_loop`.
        - Handles exceptions and logs errors.
        """
        try:
            self.get_all_pages_loop()
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_all_pages_loop(self):
        """
        Iteratively fetches all pages of logbook results:
        - Fetches the next page until no more pages remain.
        - Handles token refresh if the access token expires.
        """
        while self.next_logbook_url:
            success = self.get_next_page(self.next_logbook_url)
            if not success:
                print("Access token expired. Refreshing tokens...")
                if self.cm.refresh_tokens():
                    # Update the header with the new access token
                    self.headers["Authorization"] = f"Bearer {self.cm.tokens['access_token']}"
                    print("Retrying fetch process...")
                    self.get_all_pages_loop()  # Restart the loop (Note recursive 'clean' call)
                    return
                else:
                    print("Failed to refresh tokens. Aborting.")
                    return
            else:
                self.page += 1  # Increment the page count for next iteration of loop

    def get_next_page(self, next_page):
        try:
            print(f"Fetching page {self.page}: {next_page}")
            response = requests.get(next_page, headers=self.headers)

            # Handle 401 Invalid OAuth access token
            if response.status_code == 401:
                error_message = response.json().get("message", "")
                if error_message == "Invalid OAuth access token":
                    return False  # This will trigger token refresh then retry in get_all_pages_loop()

            # Save results to a JSON file if successful
            if response.status_code == 200:
                outfile = f"page{self.page}.json"
                with open(outfile, "w") as out:
                    json.dump(response.json(), out, indent=4)

                # Set the next page URL
                self.next_logbook_url = response.json()["meta"]["pagination"]["links"].get("next")
                return True
            else:
                response.raise_for_status()  # Raise an exception for HTTP errors

        except Exception as e:
            print(f"Error fetching page {self.page}: {str(e)}")
            self.next_logbook_url = ""  # Stop pagination on error
            return False
