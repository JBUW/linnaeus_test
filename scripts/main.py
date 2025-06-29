from linnaeus_test.database import Database
from linnaeus_test.manager import Manager
from linnaeus_test.interface import get_summarized_page

import os

if __name__ == "__main__":
    database_filename = "test.db"
    database = Database(database_filename)
    # a.export_to_csv('test.csv')
    # exit(0)
    manager = Manager(database)
    get_summarized_page(manager).launch(share=False)
