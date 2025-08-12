from linnaeus_test.manager import Manager

import gradio as gr


def is_valid_input(input: str) -> bool:
    return input.strip() != ""


def get_refresh_button(value: str, visible: bool):
    refresh_btn = gr.Button(value=value, visible=visible, elem_id="refresh-btn")
    refresh_btn.click(fn=None, js="() => { location.reload(); }")
    return refresh_btn


def get_ab_test_page(
    manager: Manager, use_case: str | None, eval_question: str | None
) -> gr.Blocks:
    page_title = "A/B-test-pagina" if use_case is None else use_case
    css = """
    .radio-group {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr;
    }
    """
    with gr.Blocks(title=page_title, css=css) as page:
        browser_storage = gr.BrowserState()
        user_session = browser_storage.storage_key

        upper_refresh_btn = get_refresh_button("Opnieuw beginnen", True)

        label = (
            "Invoertekst"
            if use_case is None
            else f"Invoertekst voor use case {use_case.lower()}"
        )
        input_box = gr.Textbox(
            label=label,
            placeholder="Dit is voorbeeldinvoer.",
        )

        model_names = ["Model A", "Model B"]
        with gr.Row():
            output_boxes = [
                gr.TextArea(
                    label=model_name,
                    visible=False,
                    interactive=False,
                    autoscroll=False,
                    show_label=True,
                    show_copy_button=True,
                )
                for model_name in model_names
            ]

        EQUAL_EVALUATION = len(model_names)
        eval_question = (
            "Welk model is beter?" if eval_question is None else eval_question
        )
        eval_radio = gr.Radio(
            [
                (model_names[0], 0),  #
                ("Even goed", EQUAL_EVALUATION),
                (model_names[1], 1),
            ],
            label=eval_question,
            elem_classes="radio-group",
            visible=False,
        )
        feedback_box = gr.Textbox(
            label="Motivatie en overige feedback",
            placeholder="<verplicht>",
            visible=False,
        )

        lower_refresh_btn = get_refresh_button("Volgende vergelijking", False)

        @gr.on(
            input_box.change,
            inputs=input_box,
            outputs=[input_box, *output_boxes],
            show_progress="hidden",
        )
        def on_input_box_change(input_text: str):
            new_visibility = is_valid_input(input_text)
            return gr.update(submit_btn="Invoeren" if new_visibility else False), *(
                gr.update(visible=new_visibility) for _ in output_boxes
            )

        @gr.on(
            input_box.submit,
            inputs=input_box,
            outputs=[input_box, *output_boxes, eval_radio],
            show_progress_on=output_boxes,
        )
        def on_input_box_submit(input_text: str):
            if is_valid_input(input_text):
                model_texts = manager.get_model_texts(user_session, input_text)
                return [
                    gr.update(
                        interactive=False, submit_btn=False, show_copy_button=True
                    ),
                    *model_texts,
                    gr.update(visible=True),
                ]
            else:
                return gr.skip()

        @gr.on(
            eval_radio.change,
            inputs=eval_radio,
            outputs=feedback_box,
            show_progress="hidden",
        )
        def on_eval_radio_change(eval_value: int | None):
            return gr.update(visible=eval_value is not None)

        @gr.on(
            feedback_box.change,
            inputs=feedback_box,
            outputs=feedback_box,
            show_progress="hidden",
        )
        def on_feedback_box_change(feedback: str):
            return gr.update(
                submit_btn="Versturen" if is_valid_input(feedback) else False
            )

        @gr.on(
            feedback_box.submit,
            inputs=[eval_radio, feedback_box, input_box, *output_boxes],
            outputs=[eval_radio, feedback_box, upper_refresh_btn, lower_refresh_btn],
        )
        def submit_evaluation(
            best_model: int,
            feedback: str,
            model_input: str,
            *model_outputs: str,
        ):
            if best_model is None:
                raise gr.Error("Geef aan welk model beter is.")
            if feedback == "":
                raise gr.Error("Motiveer de evaluatie.")
            try:
                manager.process_evaluation(
                    user_session=user_session,
                    best_model=best_model,
                    feedback=feedback,
                    model_input=model_input,
                    model_outputs=model_outputs,
                )
            except ValueError as e:
                raise gr.Error(str(e))
            gr.Info("Feedback verzonden.")
            return [
                gr.update(interactive=False),
                gr.update(interactive=False, submit_btn=False, show_copy_button=True),
                gr.update(visible=False),
                gr.update(visible=True),
            ]

    return page
