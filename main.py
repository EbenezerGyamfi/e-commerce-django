import csv
from datetime import datetime
import pandas

from finance_tracker import get_amount, get_category, get_date, get_description


class Csv:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pandas.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pandas.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }

        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)

            writer.writerow(new_entry)

        print("Entry Added successfully")

    @classmethod
    def get_transactions(cls, start_date, end_date):

        df = pandas.read_csv(cls.CSV_FILE)
        df["date"] = pandas.to_datetime(df("date"), format=Csv.FORMAT)
        start_date = datetime.strptime(start_date, Csv.FORMAT)
        end_date = datetime.strptime(end_date, Csv.FORMAT)

        mask = (df["date"]) >= start_date & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No Transactions found in the given date range")
        else:
            print(
                f"Transactions from {start_date.strftime(Csv.FORMAT)} to {end_date.strftime(Csv.FORMAT)}"
            )
            print(
                filtered_df.to_string(
                    index=False, formatters={"date": lambda x: x.strftime(Csv.FORMAT)}
                )
            )

            total_amount = filtered_df[filtered_df["catgeory"] == "Income"][
                "amount"
            ].sum()
            total_expenses = filtered_df[filtered_df["catgeory"] == "Expense"][
                "amount"
            ].sum()
            print(f"\nTotal Income: ${total_amount:.2f}")
            print(f"Total Expenses: ${total_expenses:.2f}")
            print(f"Net Income: ${total_amount - total_expenses:.2f}")


def add():
    Csv.initialize_csv()
    date = get_date(
        "Enter the date of the transaction (dd-mm-yy) or enter for today's date: ",
        allow_default=True,
    )
    amount = get_amount()
    category = get_category()
    description = get_description()
    Csv.add_entry(date, amount, category, description)


add()
