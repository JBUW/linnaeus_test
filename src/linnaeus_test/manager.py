from linnaeus_test.database import Database


class Manager:
    def __init__(self, database: Database):
        self.database = database
        self.session_to_models = {}

    def get_model_texts(self, user_session, text):
        models = self.get_models(user_session)
        result = [f"Model {models[0]} <- {text}", f"Model {models[1]} <- {text}"]
        return result

    def get_models(self, user_session):
        if user_session in self.session_to_models:
            *models, processed_feedback = self.session_to_models[user_session]
            if processed_feedback:
                self.session_to_models[user_session] = [
                    models[0] + 2,
                    models[1] + 2,
                    False,
                ]
        else:
            self.session_to_models[user_session] = [0, 1, False]
        return self.session_to_models[user_session]

    def process_feedback(self, user_session, eval, feedback):
        if user_session not in self.session_to_models:
            return
        *models, processed_feedback = self.session_to_models[user_session]
        if eval in (0, 1):
            print(
                f"{'Updated' if processed_feedback else 'New'}: {models[eval]} is better."
            )
        self.session_to_models[user_session][2] = True
        self.database.add_evaluation(user_session, models[0], models[1], eval, feedback)
        self.database.export_to_csv("test.csv")
