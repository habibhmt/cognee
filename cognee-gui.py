import sys
import asyncio
import os
from dotenv import load_dotenv, set_key

try:
    import cognee
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QPushButton,
        QLineEdit,
        QFileDialog,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QTextEdit,
        QProgressDialog,
        QDialog,
        QFormLayout,
        QDialogButtonBox,
    )
    from PySide6.QtCore import Qt

    from qasync import QEventLoop  # Import QEventLoop from qasync
except ImportError as e:
    print(
        "\nPlease install Cognee with optional gui dependencies or manually install missing dependencies.\n"
    )
    print("\nTo install with poetry use:")
    print("\npoetry install -E gui\n")
    print("\nOr to install with poetry and all dependencies use:")
    print("\npoetry install --all-extras\n")
    print("\nTo install with pip use: ")
    print('\npip install ".[gui]"\n')
    raise e


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LLM Settings")
        self.setMinimumWidth(400)

        self.layout = QFormLayout(self)

        self.llm_provider_input = QLineEdit(self)
        self.llm_model_input = QLineEdit(self)
        self.llm_endpoint_input = QLineEdit(self)
        self.llm_api_key_input = QLineEdit(self)
        self.llm_api_key_input.setEchoMode(QLineEdit.Password) # Hide API key

        self.layout.addRow("LLM Provider:", self.llm_provider_input)
        self.layout.addRow("LLM Model:", self.llm_model_input)
        self.layout.addRow("LLM Endpoint:", self.llm_endpoint_input)
        self.layout.addRow("LLM API Key:", self.llm_api_key_input)

        self.load_settings()

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_settings)
        self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)

    def load_settings(self):
        load_dotenv() # Load .env file
        self.llm_provider_input.setText(os.getenv("LLM_PROVIDER", "custom"))
        self.llm_model_input.setText(os.getenv("LLM_MODEL", "openrouter/mistralai/mistral-7b-instruct:free")) # OpenRouter model format
        self.llm_endpoint_input.setText(os.getenv("LLM_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions"))
        self.llm_api_key_input.setText(os.getenv("LLM_API_KEY", "")) # Still use LLM_API_KEY for cognee's internal config

    def save_settings(self):
        try:
            # Ensure .env file exists or create it
            env_path = os.path.join(os.getcwd(), ".env")
            if not os.path.exists(env_path):
                open(env_path, 'a').close() # Create empty .env file if it doesn't exist

            set_key(env_path, "LLM_PROVIDER", self.llm_provider_input.text())
            set_key(env_path, "LLM_MODEL", self.llm_model_input.text())
            set_key(env_path, "LLM_ENDPOINT", self.llm_endpoint_input.text())
            # For OpenRouter, litellm expects OPENROUTER_API_KEY and OPENROUTER_API_BASE
            set_key(env_path, "OPENROUTER_API_KEY", self.llm_api_key_input.text())
            set_key(env_path, "OPENROUTER_API_BASE", self.llm_endpoint_input.text())
            # Also keep LLM_API_KEY for cognee's internal config if it uses it directly
            set_key(env_path, "LLM_API_KEY", self.llm_api_key_input.text())
            QMessageBox.information(self, "Settings Saved", "LLM settings have been saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

class FileSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.load_llm_settings() # Load settings on app start
        self.init_ui()

    def load_llm_settings(self):
        load_dotenv() # Load .env file
        # These will be used by cognee internally if set as environment variables
        os.environ["LLM_PROVIDER"] = os.getenv("LLM_PROVIDER", "custom")
        os.environ["LLM_MODEL"] = os.getenv("LLM_MODEL", "openrouter/mistralai/mistral-7b-instruct:free") # OpenRouter model format
        os.environ["LLM_ENDPOINT"] = os.getenv("LLM_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
        os.environ["LLM_API_KEY"] = os.getenv("LLM_API_KEY", "")

        # Set OpenRouter specific environment variables for LiteLLM
        os.environ["OPENROUTER_API_KEY"] = os.getenv("LLM_API_KEY", "")
        os.environ["OPENROUTER_API_BASE"] = os.getenv("LLM_ENDPOINT", "https://openrouter.ai/api/v1")

    def init_ui(self):
        # Horizontal layout for file upload, visualization, and settings buttons
        button_layout = QHBoxLayout()

        # Button to open file dialog
        self.file_button = QPushButton("Upload File to Cognee", parent=self)
        self.file_button.clicked.connect(self.open_file_dialog)
        button_layout.addWidget(self.file_button)

        # Button to visualize data
        self.visualize_button = QPushButton("Visualize Data", parent=self)
        self.visualize_button.clicked.connect(lambda: asyncio.ensure_future(self.visualize_data()))
        button_layout.addWidget(self.visualize_button)

        # Button to open settings dialog
        self.settings_button = QPushButton("Settings", parent=self)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        button_layout.addWidget(self.settings_button)

        # Label to display selected file path
        self.file_label = QLabel("No file selected", parent=self)

        # Line edit for search input
        self.search_input = QLineEdit(parent=self)
        self.search_input.setPlaceholderText("Enter text to search...")

        # Button to perform search; schedule the async search on click
        self.search_button = QPushButton("Cognee Search", parent=self)
        self.search_button.clicked.connect(lambda: asyncio.ensure_future(self._cognee_search()))

        # Text output area for search results
        self.result_output = QTextEdit(parent=self)
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Search results will appear here...")

        # Progress dialog
        self.progress_dialog = QProgressDialog("Processing..", None, 0, 0, parent=self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)  # Remove the cancel button
        self.progress_dialog.close()

        # Layout setup
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.file_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.result_output)

        self.setLayout(layout)
        self.setWindowTitle("Cognee")
        self.resize(500, 300)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_llm_settings() # Reload settings after dialog is closed

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a File", "", "All Files (*.*);;Text Files (*.txt)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected: {file_path}")
            asyncio.ensure_future(self.process_file_async())

    async def process_file_async(self):
        """Asynchronously add and process the selected file."""
        # Disable the entire window
        self.progress_dialog.show()
        self.setEnabled(False)
        try:
            await cognee.add(self.selected_file)
            await cognee.cognify()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"File processing failed: {str(e)}")
        # Once finished, re-enable the window
        self.setEnabled(True)
        self.progress_dialog.close()

    async def _cognee_search(self):
        """Performs an async search and updates the result output."""
        # Disable the entire window
        self.setEnabled(False)
        self.progress_dialog.show()

        try:
            search_text = self.search_input.text().strip()
            result = await cognee.search(query_text=search_text)
            print(result)
            # Assuming result is a list-like object; adjust if necessary
            self.result_output.setText(result[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

        # Once finished, re-enable the window
        self.setEnabled(True)
        self.progress_dialog.close()

    async def visualize_data(self):
        """Async slot for handling visualize data button press."""
        import webbrowser
        from cognee.api.v1.visualize.visualize import visualize_graph
        import os
        import pathlib

        html_file = os.path.join(pathlib.Path(__file__).parent, ".data", "graph_visualization.html")
        await visualize_graph(html_file)
        webbrowser.open(f"file://{html_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Create a qasync event loop and set it as the current event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = FileSearchApp()
    window.show()

    with loop:
        loop.run_forever()
