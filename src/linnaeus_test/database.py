from linnaeus_test.llm_base import LLMBase

import contextlib
import json
import logging
import os
import pandas as pd
import sqlite3
from typing import Final


class Database:
    MODEL_PRESET_TABLE_NAME: Final[str] = "model_preset"
    MODEL_PRESET_COLUMNS: Final[dict[str, str]] = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "model": "TEXT NOT NULL",
        "parameters": "JSON",
        "system_message": "TEXT",
    }

    EVAL_TABLE_NAME: Final[str] = "user_evaluation"
    BEST_MODEL_DB_REPRS: Final[list[str]] = ["A", "B", "="]
    EQUAL_MODEL_EVAL: Final[int] = len(BEST_MODEL_DB_REPRS) - 1
    EVAL_COLUMNS: Final[dict[str, str]] = {
        "user_session": "TEXT NOT NULL",
        "model_preset_id_a": "INTEGER NOT NULL",
        "model_preset_id_b": "INTEGER NOT NULL",
        "best_model": f"CHAR(1) CHECK (best_model IN ({', '.join(f"'{x}'" for x in BEST_MODEL_DB_REPRS)}))",
        "feedback": "TEXT NOT NULL",
        "model_input": "TEXT NOT NULL",
        "model_a_output": "TEXT NOT NULL",
        "model_b_output": "TEXT NOT NULL",
    }

    def __init__(self, db: str | None = None, force_creation: bool = False):
        create_db = True
        if db is None:
            self.db = ":memory:"
        else:
            self.db = db
            if os.path.exists(self.db):
                if force_creation:
                    os.remove(self.db)
                else:
                    create_db = False
        if create_db:
            with contextlib.closing(sqlite3.connect(self.db)) as connection:
                connection.set_trace_callback(logging.debug)
                model_preset_column_string = ", ".join(
                    f"{name} {definition}"
                    for name, definition in __class__.MODEL_PRESET_COLUMNS.items()
                )
                unique_string = ", ".join(
                    name
                    for name in __class__.MODEL_PRESET_COLUMNS.keys()
                    if name != "id"
                )
                connection.execute(
                    f"CREATE TABLE {__class__.MODEL_PRESET_TABLE_NAME}({model_preset_column_string}, UNIQUE ({unique_string}))"
                )
                eval_column_string = ", ".join(
                    f"{name} {definition}"
                    for name, definition in __class__.EVAL_COLUMNS.items()
                )
                connection.execute(
                    f"CREATE TABLE {__class__.EVAL_TABLE_NAME}(Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, {eval_column_string})"
                )

    def add_evaluation(self, model_presets: tuple[LLMBase, LLMBase], **eval_data):
        eval_data["model_preset_id_a"], eval_data["model_preset_id_b"] = [
            self.get_model_preset_id(model_preset) for model_preset in model_presets
        ]
        eval_data["best_model"] = self.get_best_model_db_repr(eval_data["best_model"])
        eval_data["model_a_output"], eval_data["model_b_output"] = eval_data[
            "model_outputs"
        ]
        del eval_data["model_outputs"]
        with contextlib.closing(sqlite3.connect(self.db)) as connection:
            connection.set_trace_callback(logging.debug)
            with connection:
                connection.execute(
                    f"INSERT INTO {__class__.EVAL_TABLE_NAME} ({', '.join(eval_data.keys())}) VALUES ({', '.join('?' for _ in eval_data)})",
                    tuple(eval_data.values()),
                )

    @staticmethod
    def get_best_model_db_repr(best_model: int | None) -> str:
        best_model_index = (
            best_model if best_model in (0, 1) else __class__.EQUAL_MODEL_EVAL
        )
        return __class__.BEST_MODEL_DB_REPRS[best_model_index]

    def get_model_preset_id(self, model_preset: LLMBase) -> int:
        with contextlib.closing(sqlite3.connect(self.db)) as connection:
            connection.set_trace_callback(logging.debug)
            columns = {
                "model": model_preset.model,
                "parameters": json.dumps(model_preset.model_params),
                "system_message": model_preset.system_message,
            }
            ids = connection.execute(
                f"SELECT id FROM {__class__.MODEL_PRESET_TABLE_NAME} WHERE {" AND ".join(f'{k} = ?' for k in columns.keys())}",
                tuple(columns.values()),
            ).fetchone()
            if ids is None:
                with connection:
                    return connection.execute(
                        f"INSERT INTO {__class__.MODEL_PRESET_TABLE_NAME} ({', '.join(columns.keys())}) VALUES ({', '.join('?' for _ in columns)})",
                        tuple(columns.values()),
                    ).lastrowid
            else:
                return ids[0]

    def model_preset_to_json(self, output_json: str | None = None):
        with contextlib.closing(sqlite3.connect(self.db)) as connection:
            connection.set_trace_callback(logging.debug)
            df = pd.read_sql(
                f"SELECT * FROM {__class__.MODEL_PRESET_TABLE_NAME}",
                connection,
                index_col="id",
            )
        # Decode the parameters column from JSON string to proper JSON structure
        df["parameters"] = df["parameters"].apply(
            lambda x: json.loads(x) if x else None
        )
        return df.to_json(output_json, orient="index", indent=2)

    def eval_to_csv(self, output_csv: str | None = None):
        """
        Exports the specified table to a CSV file.

        Args:
            table_name (str): Name of the table to export.
            output_csv (str): Path to the output CSV file.
        """
        return self.sql_table_to_csv(self.db, __class__.EVAL_TABLE_NAME, output_csv)

    @staticmethod
    def sql_table_to_csv(database: str, table_name: str, output_csv: str | None):
        """
        Exports a specified table from the database to a CSV file.

        Args:
            database (str): Path to the SQLite database file.
            table_name (str): Name of the table to export.
            output_csv (str): Path to the output CSV file.
        """
        with contextlib.closing(sqlite3.connect(database)) as connection:
            connection.set_trace_callback(logging.debug)
            return pd.read_sql(f"SELECT * FROM {table_name}", connection).to_csv(
                output_csv, index=False
            )
