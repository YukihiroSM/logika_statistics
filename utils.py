import phonenumbers
import pandas as pd
import library

def format_number(number: str):
    """
    Formats any case of phone number into number like: 380XXYYYYYYY
    Input: number as str
        (tested formats: ["380981231234", "380 98 123 12 34", "'+380 (50) 123-12-34", "0951231234", "+380981231234"])
    Output: number as string by template: 380501231234
    """
    try:
        formatted_number = phonenumbers.format_number(
            phonenumbers.parse(number, "UA"),
            phonenumbers.PhoneNumberFormat.E164
        ).replace("+", "")
    except:
        try:
            formatted_number = phonenumbers.format_number(
                phonenumbers.parse(number.split()[0], "UA"),
                phonenumbers.PhoneNumberFormat.E164
            ).replace("+", "")
        except:
            try:
                formatted_number = phonenumbers.format_number(
                    phonenumbers.parse(number.split(",")[0], "UA"),
                    phonenumbers.PhoneNumberFormat.E164
                ).replace("+", "")
            except:
                return None
    return formatted_number


def clean_numbers(df: pd.DataFrame, destination_column, numbers_columns):
    for index, row in df.iterrows():
        possible_numbers = [format_number(str(row[col])) for col in numbers_columns if len(str(row[col])) > 8]
        if len(possible_numbers) == 0:
            df.at[index, destination_column] = None
        else:
            df.at[index, destination_column] = possible_numbers[0]
    return df


def clean_same_columns_values(df, col1, col2, destination_column):
    for index, row in df.iterrows():
        if row[col1] is None and not (row[col2] is None):
            df.at[index, destination_column] = row[col2]
        elif row[col2] is None and not (row[col1] is None):
            df.at[index, destination_column] = row[col1]
        elif not (row[col1] is None) and not (row[col2] is None):
            if len(row[col1]) > 2:
                df.at[index, destination_column] = row[col1]
            else:
                df.at[index, destination_column] = row[col2]
        else:
            df.at[index, destination_column] = None
    return df


def get_course(course):
    if course is None:
        return None
    for c in library.COURSES["programming"]:
        if course.replace("-", "_").replace(" ", "_").replace('"', "'").lower() in library.COURSES["programming"][c]:
            return c
    return None


def get_region(region):
    if region is None:
        return None
    for r in library.REGIONS:
        if region.replace("-", "_").replace(" ", "_").lower() in library.REGIONS[r]["titles"]:
            return r
    return None
