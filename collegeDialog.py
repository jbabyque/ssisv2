from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFormLayout, QHBoxLayout, QMessageBox)
import mysql.connector
from mysql.connector import Error
import logging

class CollegeDialog(QDialog):
    def __init__(self, parent=None, college=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit College")
        self.layout = QVBoxLayout(self)
        self.college = college
        self.conn = parent.conn if parent else None  # Get connection from parent

        self.form_layout = QFormLayout()
        self.college_code = QLineEdit(self)
        self.college_name = QLineEdit(self)

        self.form_layout.addRow("College Code:", self.college_code)
        self.form_layout.addRow("College Name:", self.college_name)

        self.layout.addLayout(self.form_layout)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)

        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

        if college:
            self.college_code.setText(college["College Code"])
            self.college_name.setText(college["College Name"])

    def validate_and_accept(self):
        if not self.college_code.text() or not self.college_name.text():
            QMessageBox.warning(self, "Validation Error", 
                              "Both College Code and Name are required!")
            return
        
        if self.validate_college_code():
            self.accept()

    def validate_college_code(self):
        if not self.conn:
            QMessageBox.critical(self, "Database Error", 
                                "No database connection available")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Check if college code already exists (for new entries)
            if not self.college:
                cursor.execute(
                    "SELECT college_code FROM colleges WHERE college_code = %s",
                    (self.college_code.text(),)
                )
                if cursor.fetchone():
                    QMessageBox.warning(self, "Duplicate Code", 
                                      "College Code already exists!")
                    return False
            
            return True
            
        except Error as e:
            logging.error("Database error during validation: %s", e)
            QMessageBox.critical(self, "Database Error", 
                               f"Error validating college: {e}")
            return False

    def get_college_data(self):
        return {
            "college_code": self.college_code.text(),
            "college_name": self.college_name.text()
        }