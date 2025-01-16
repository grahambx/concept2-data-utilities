import os
import json
import pandas as pd
from datetime import datetime, timedelta


class RowingDataProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder

    def process(self):
        """Process the JSON files to generate the output CSVs."""
        # Load data from JSON files
        data_df = self.load_data()

        # Save raw data to CSV and Excel
        self.save_as_csv(data_df, 'rowing_data.csv')
        print("rowing_data.csv updated")
        self.save_as_excel(data_df, 'rowing_data.xlsx')
        print("rowing_data.xlsx updated")

        # Aggregate weekly data and save to CSV
        weekly_df = self.aggregate_weekly(data_df)
        self.save_as_csv(weekly_df, 'weekly-report.csv')
        print("weekly-report.csv updated")
        self.save_as_excel(weekly_df, 'weekly-report.xlsx')
        print("weekly-report.xlsx updated")

    def load_data(self):
        """Load all JSON files in the input folder into a single pandas DataFrame."""
        all_data = []
        for file_name in sorted(os.listdir(self.input_folder)):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.input_folder, file_name)
                with open(file_path, 'r') as file:
                    data = json.load(file).get("data", [])
                    all_data.extend(data)
        return pd.DataFrame(all_data)

    def save_as_csv(self, df, file_name):
        """Save a DataFrame as a CSV file in the output folder."""
        output_path = os.path.join(self.output_folder, file_name)
        df.to_csv(output_path, index=False)

    def save_as_excel(self, df, file_name):
        """Save a DataFrame as an Excel file in the output folder."""
        output_path = os.path.join(self.output_folder, file_name)
        df.to_excel(output_path, index=False, engine="openpyxl")

    def aggregate_weekly(self, df):
        """Aggregate data by week (Saturday to Friday)."""
        df['date'] = pd.to_datetime(df['date'])  # Ensure date is a datetime object
        df = df.sort_values(by='date')

        # Define the current week ending date (upcoming Friday)
        current_week_end = datetime.now()
        while current_week_end.weekday() != 4:  # Find the upcoming Friday
            current_week_end += timedelta(days=1)

        # Define the earliest date in the data
        earliest_date = df['date'].min()

        # Align earliest date to the previous Saturday
        start_date = earliest_date - timedelta(days=(earliest_date.weekday() + 2) % 7)

        # Create weekly intervals
        weeks = []
        while start_date <= current_week_end:
            week_end = start_date + timedelta(days=6)  # Saturday + 6 days = Friday
            weeks.append((start_date, week_end))
            start_date = week_end + timedelta(days=1)

        # Aggregate data by week
        weekly_data = []
        for week_start, week_end in reversed(weeks):  # Most recent week first
            week_mask = (df['date'] >= week_start) & (df['date'] <= week_end)
            week_data = df[week_mask]
            distance_total = week_data['distance'].sum()
            calories_total = week_data['calories_total'].sum()
            sessions = len(week_data)  # total number of records per week

            weekly_data.append({
                'Start-Saturday': week_start.strftime('%d/%m/%Y'),
                'End-Friday': week_end.strftime('%d/%m/%Y'),
                'sessions': sessions,
                'distance_total': int(distance_total),
                'calories_total': int(calories_total)
            })

        return pd.DataFrame(weekly_data)
