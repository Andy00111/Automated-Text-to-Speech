import sys
import os
import pyttsx3
import wave
import array
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QFileDialog, 
                            QLabel, QMessageBox, QComboBox)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class TTSApp(QMainWindow):
    CSS = """
    QMainWindow {
        background-color: #2b2b2b;
    }
    QTextEdit {
        background-color: #3b3b3b;
        color: #ffffff;
        border: 2px solid #4b4b4b;
        border-radius: 5px;
        padding: 5px;
        font-size: 14px;
    }
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        min-width: 120px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #0b5ed7;
    }
    QPushButton:disabled {
        background-color: #666666;
    }
    QLabel {
        color: white;
        font-size: 16px;
    }
    QComboBox {
        background-color: #3b3b3b;
        color: white;
        border: 2px solid #4b4b4b;
        border-radius: 5px;
        padding: 5px;
        min-width: 150px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid none;
        border-right: 5px solid none;
        border-top: 5px solid white;
        width: 0;
        height: 0;
        margin-right: 5px;
    }
    """

    def __init__(self):
        super().__init__()
        self.generated_audio = None
        self.temp_file = None
        self.engine = pyttsx3.init()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Text to Speech Converter")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(self.CSS)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Add title label
        title_label = QLabel("Text to Speech Converter")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; margin: 20px 0;")
        layout.addWidget(title_label)

        # Voice selection
        voice_layout = QHBoxLayout()
        voice_label = QLabel("Select Voice:")
        voice_label.setStyleSheet("margin-right: 10px;")
        self.voice_combo = QComboBox()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            self.voice_combo.addItem(voice.name, voice.id)
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addStretch()
        layout.addLayout(voice_layout)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speech Rate:")
        speed_label.setStyleSheet("margin-right: 10px;")
        self.speed_combo = QComboBox()
        for speed in ['Slow', 'Normal', 'Fast']:
            self.speed_combo.addItem(speed)
        self.speed_combo.setCurrentText('Normal')
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_combo)
        speed_layout.addStretch()
        layout.addLayout(speed_layout)

        # Add text input area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to convert to speech...")
        layout.addWidget(self.text_input)

        # Button layout
        button_layout = QHBoxLayout()
        
        # Convert button
        self.convert_button = QPushButton("Convert to Speech")
        self.convert_button.clicked.connect(self.convert_text)
        button_layout.addWidget(self.convert_button)

        # Export button
        self.export_button = QPushButton("Export Audio")
        self.export_button.clicked.connect(self.export_audio)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)

        # Clear button
        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("Ready to convert text to speech")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("margin-top: 20px;")
        layout.addWidget(self.status_label)

    def convert_text(self):
        text = self.text_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text to convert.")
            return

        try:
            self.status_label.setText("Converting text to speech...")
            QApplication.processEvents()

            # Set voice
            voice_id = self.voice_combo.currentData()
            self.engine.setProperty('voice', voice_id)

            # Set speed
            speed_setting = self.speed_combo.currentText()
            speed_values = {'Slow': 150, 'Normal': 200, 'Fast': 250}
            self.engine.setProperty('rate', speed_values[speed_setting])

            # Create a temporary file
            if self.temp_file:
                os.unlink(self.temp_file)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tf:
                self.temp_file = tf.name

            # Save audio to temporary file
            self.engine.save_to_file(text, self.temp_file)
            self.engine.runAndWait()

            self.status_label.setText("Conversion complete! You can now export the audio.")
            self.export_button.setEnabled(True)

        except Exception as e:
            self.status_label.setText(f"Error during conversion: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to convert text to speech.")

    def export_audio(self):
        if not self.temp_file or not os.path.exists(self.temp_file):
            QMessageBox.warning(self, "Warning", "No audio generated yet.")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Audio",
            os.path.expanduser("~/Desktop/output.wav"),
            "WAV Files (*.wav);;All Files (*.*)"
        )

        if file_name:
            try:
                # Copy the temporary file to the desired location
                with open(self.temp_file, 'rb') as source:
                    with open(file_name, 'wb') as target:
                        target.write(source.read())
                self.status_label.setText(f"Audio saved successfully to: {file_name}")
            except Exception as e:
                self.status_label.setText(f"Error saving audio: {str(e)}")
                QMessageBox.critical(self, "Error", "Failed to save audio file.")

    def clear_text(self):
        self.text_input.clear()
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except:
                pass
        self.temp_file = None
        self.export_button.setEnabled(False)
        self.status_label.setText("Ready to convert text to speech")

    def closeEvent(self, event):
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except:
                pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = TTSApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()