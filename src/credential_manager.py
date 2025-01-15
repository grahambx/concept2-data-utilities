import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class CredentialManager:
    def __init__(self):
        """
        Manages OAuth2.0 credentials:
        - Loads environment variables for client credentials.
        - Initializes tokens by either loading them or obtaining new ones.
        """
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.oauth_auth_code = os.getenv("OAUTH_AUTH_CODE")
        self.scope = "user:read,results:read"
        self.redirect_uri = "http://localhost/callback"
        self.token_url = "https://log.concept2.com/oauth/access_token"
        self.token_file = "credentials.json"
        self.tokens = {}

        # Validate required environment variables pulled through
        if not all([self.client_id, self.client_secret, self.oauth_auth_code]):
            raise ValueError("Missing one or more required environment value in .env file")

        # Load or initialise tokens
        self.load_tokens()

    def load_tokens(self):
        """Load tokens from the file if they exist, or initialize if they don't."""
        if not self.check_tokens_exist():
            # If tokens do not exist, attempt to initialize them
            print("Attempting to authenticate for new tokens...")
            if not self.initialise_tokens():
                raise Exception("Failed to create tokens after OAuth2.0 authentication.")
        else:
            with open(self.token_file, "r") as file:  # TODO - why open and json.load here and in check_tokens_exist()
                self.tokens = json.load(file)
            print(f"Tokens loaded from {self.token_file}")

    def check_tokens_exist(self):
        """
        Checks if the credentials file exists and contains valid tokens.
        :return: True if valid tokens exist, False otherwise.
        """
        if not os.path.exists(self.token_file):
            print("Credential File for tokens do not exist")
            return False
        try:
            with open(self.token_file, "r") as file:
                tokens = json.load(file)
                # Check if both 'access_token' and 'refresh_token' are present and non-empty
                check = bool(tokens.get("access_token")) and bool(tokens.get("refresh_token"))
                if not check:
                    print("No tokens stored in Credential File")
                else:
                    print("Existing Authentication tokens Found for Concept2 logbook API")
                return check
        except (json.JSONDecodeError, IOError):
            return False

    def initialise_tokens(self):
        """
        Obtains and saves initial tokens using the OAuth2.0 authentication code.
        :return: True if successful, raises Exception otherwise.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": self.oauth_auth_code,
            "scope": self.scope
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(tokens["access_token"], tokens["refresh_token"])
            print("Authorization successful, tokens obtained.")
            return True
        else:
            raise Exception(f"Failed to fetch tokens: {response.status_code} - {response.text}")

    def save_tokens(self, access_token, refresh_token):
        """
        Saves the tokens to a file.
        :param access_token: The access token.
        :param refresh_token: The refresh token.
        """
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        with open(self.token_file, "w") as file:
            json.dump(tokens, file, indent=4)
        self.tokens = tokens
        print(f"Tokens saved to {self.token_file}.")

    def refresh_tokens(self):
        """
        Refreshes the access token using the refresh token.
        :return: True if the refresh was successful and new tokens are saved.
        """
        if not self.tokens or not self.tokens.get("refresh_token"):
            raise Exception("No valid refresh token available for refresh process.")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.tokens["refresh_token"]
        }

        try:
            response = requests.post(self.token_url, data=data)
            if response.status_code == 200:
                tokens = response.json()
                self.save_tokens(tokens["access_token"], tokens["refresh_token"])
                print("Tokens refreshed successfully.")
                return True
            else:
                raise Exception(f"Failed to refresh tokens: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            raise Exception(f"Error refreshing tokens: {e}")
