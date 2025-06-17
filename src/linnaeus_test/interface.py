# %%script false --no-raise-error
import gradio as gr


def run(share=True):
    custom_css = """
    .my_radio .gradio-radio label {
    display:block;
    width:100%;
    box-sizing: border-box;
    padding:0.5em;
    text-align: center;
    }
    """
    css = """
    h1 {
        text-align: center;
        display:block;
    }
    """
    css = """
    .radio-group {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr;
    }
    """
    with gr.Blocks(css=css) as demo:
        input_box = gr.Textbox(label="Invoer")
        input_submit_button = gr.Button("Uitvoer")

        model_names = ["Model A", "Model B"]

        def llm_output(text):
            return [model_name + ": " + text for model_name in model_names]

        with gr.Row():
            output_boxes = [gr.Textbox(label=model_name) for model_name in model_names]
        input_submit_button.click(fn=llm_output, inputs=input_box, outputs=output_boxes)
        radio = gr.Radio(
            [model_names[0], "Even goed", model_names[1]],
            label="Welke uitvoer is beter?",
            elem_classes="radio-group",
        )

    demo.launch(share=share)
