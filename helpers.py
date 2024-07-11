from flask import redirect, render_template, request, session, send_file
import pandas as pd


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", error_code=code, error_message=escape(message)), code

def upload_to_excel(path: str, data, sheet_name):

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    # Write the combined DataFrame back to the Excel file
    df.to_excel(path, sheet_name=sheet_name, index=False)
    print(f"Data saved to {path}")
