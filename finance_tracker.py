from datetime import datetime
from sre_parse import CATEGORIES

date_format = "%d-%m-%Y"
CATEGORIES = {"I": "income", "E": "expense"}


def get_date(prompt, allow_default=False):
    date_str = input(prompt)
    if allow_default and not date_str:
        return datetime.today().strftime(date_format)

    try:
        valid_date = datetime.strptime(date_str, date_format)
        return valid_date.strftime(date_format)
    except ValueError:
        print("Invalid date format. Please use dd-mm-yyyy.")
        return get_date(prompt, allow_default)


def get_amount():
    try:
        amount = float(input("Enter the amount: "))

        if amount <= 0:
            raise ValueError("Amount must be a non-negative non-zeror value")
        return amount
    except ValueError as error:
        print(error)
        return get_amount()


def get_category():
    category = input("Enter the category ('I' for Income or 'E' for Expense)").upper()
    if category in CATEGORIES:
        return CATEGORIES[category]
    print("Invalid category. please enter 'I' for Income and 'E' for Expense")
    return get_category()


def get_description():
    return input("Enter a description ")
