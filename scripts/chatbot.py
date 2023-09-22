from typing import Optional
import openai
from ipywidgets.widgets import Button, Textarea, Layout, HTML, VBox, HBox, Label
from markdown import markdown

openai.api_key = # Your Key

STYLE = HTML(
    """
    <style>
      .label {
        background-color: transparent!important;
        width:200px;
        font-weight: bold;
      }
      .message{
        line-height: 5px;
      }
      .background{
        background-color: white;
      }
    </style>
    """
)


def sanitize_code(code: str) -> str:
    return (
        code.replace("```python", "<code>")
        .replace("```", "</code>")
        .replace("<code>", "<pre><code>")
        .replace("</code>", "</code></pre>")
    )


def create_label(label: str) -> HTML:
    label_element = HTML(
        value=label,
    )
    label_element.add_class("label")
    return label_element


def add_label(label: str, element: HTML) -> HBox:
    box = HBox(
        [
            create_label(label),
            element,
        ],
        style=dict(
            background_color="grey!important", border_style="solid", border_width="2px"
        ),
    )
    box.add_class("background")
    return box


class Chat:
    def __init__(self, prompt: Optional[str] = None, model: str = "gpt-4-0314"):
        self.model = model
        self.history = []
        if prompt:
            self.history.append({"role": "user", "content": prompt})

        self.user_input = Textarea(
            value="",
            disabled=False,
            layout=Layout(height="170px", width="100%"),
        )

        self.submit_button = Button(
            description="Submit",
            disabled=False,
            button_style="success",
            tooltip="Click to submit",
            icon="check",
        )
        self.submit_button.layout.display = "block"
        self.submit_button.layout.margin = "10px auto"
        self.submit_button.layout.width = "100%"
        self.submit_button.on_click(self.get_user_input)

        self.answer = HTML(value="", placeholder="")

        self.dialog = VBox(
            [
                STYLE,
                add_label("✍ Your message:", self.user_input),
                self.submit_button,
                add_label("🤖 Bot - current answer:", self.answer),
            ]
        )
        self.dialog.add_class("background")

    def add_message(self, role: str, message: str) -> None:
        inside_message = HTML(value=sanitize_code(markdown(message)))
        inside_message.add_class("message")
        self.dialog.children = (
            self.dialog.children[:-3]
            + (
                add_label(
                    role,
                    inside_message,
                ),
            )
            + self.dialog.children[-3:]
        )

    def get_user_input(self, b) -> None:
        message = self.user_input.value
        self.add_message("👨‍🚀 You:", message)

        self.history.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model=self.model, messages=self.history, temperature=0, stream=True
        )
        collected_messages = []
        current_reply = None
        for chunk in response:
            chunk_message = chunk["choices"][0].get("delta", {}).get("content")
            if chunk_message is not None:
                collected_messages.append(chunk_message)
                current_reply = "".join(collected_messages)
                self.answer.value = sanitize_code(markdown(current_reply))
        self.answer.value = ""
        self.add_message("🤖 Bot:", current_reply)
        self.history.append({"role": "system", "content": current_reply})
        return

    def show(self):
        return self.dialog
