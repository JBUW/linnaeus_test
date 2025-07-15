import os
import pandas as pd
import sqlite3


class Database:
    table_name = "user_evaluation"
    columns = {
        "user_session": "TEXT NOT NULL",
        "model_a": "INTEGER NOT NULL",
        "model_b": "INTEGER NOT NULL",
        "best_model": "CHAR(1) CHECK (best_model IN ('A', 'B', '='))",
        "feedback": "TEXT",
    }

    def __init__(self, db=None, force_creation=False):
        if db is None:
            self.db = ":memory:"
            create_db = True
        else:
            self.db = db
            create_db = True
            if os.path.exists(self.db):
                if force_creation:
                    os.remove(self.db)
                else:
                    create_db = False
        if create_db:
            connection = sqlite3.connect(self.db)
            connection.execute(
                f"CREATE TABLE {__class__.table_name}({', '.join(f"{name} {definition}" for name, definition in __class__.columns.items())}, Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )

    def add_evaluation(self, user_session, model_a, model_b, best_model, feedback):
        """
        Adds a new evaluation to the database.

        Args:
            user_session (str): Unique identifier for the user session.
            model_a (str): Identifier for model A.
            model_b (str): Identifier for model B.
            best_model (str): Identifier for the best model chosen by the user.
            feedback (str): Feedback provided by the user.
        """
        connection = sqlite3.connect(self.db)
        with connection:
            connection.execute(
                f"INSERT INTO {__class__.table_name} ({', '.join(__class__.columns.keys())}) VALUES (?, ?, ?, ?, ?)",
                (user_session, model_a, model_b, "AB="[best_model], feedback),
            )
        connection.close()

    def export_to_csv(self, output_csv, table_name=table_name):
        """
        Exports the specified table to a CSV file.

        Args:
            table_name (str): Name of the table to export.
            output_csv (str): Path to the output CSV file.
        """
        connection = sqlite3.connect(self.db)
        pd.read_sql(f"SELECT * FROM {table_name}", connection).to_csv(
            output_csv, index=False
        )
        connection.close()
