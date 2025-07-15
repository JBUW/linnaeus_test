# %%script false --no-raise-error
from linnaeus_test.manager import Manager

import gradio as gr


def get_summarized_page(manager: Manager):
    css = """
    .radio-group {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr;
    }
    """
    with gr.Blocks(css=css) as page:
        browser_storage = gr.BrowserState()
        user_session = browser_storage.storage_key
        input_box = gr.Textbox(
            label="Tekst",
            placeholder="Dit is een voorbeeldtekst.",
            submit_btn="Vat samen",
        )

        model_names = ["Model A", "Model B"]
        with gr.Row():
            output_boxes = [gr.Textbox(label=model_name) for model_name in model_names]

        @gr.on(input_box.submit, inputs=input_box, outputs=output_boxes)
        def get_model_texts(text: str):
            if text == "":
                return gr.skip()
            model_texts = manager.get_model_texts(user_session, text)
            return model_texts

        EQUAL_EVALUATION = len(model_names)
        eval_radio = gr.Radio(
            [
                (model_names[0], 0),  #
                ("Even goed", EQUAL_EVALUATION),
                (model_names[1], 1),
            ],
            label="Welk model geeft een betere samenvatting?",
            elem_classes="radio-group",
        )
        feedback_box = gr.Textbox(
            label="Feedback", placeholder="<verplicht>", submit_btn="Stuur"
        )

        @gr.on(feedback_box.submit, inputs=[eval_radio, feedback_box])
        def submit_feedback(eval: int, feedback: str):
            if eval is None:
                raise gr.Error("Geef aan welk model beter is.")
            if feedback == "":
                raise gr.Error("Motiveer de evaluatie.")
            print(eval, feedback)
            manager.process_feedback(user_session, eval, feedback)

    return page
