from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFormLayout, QHBoxLayout, QMessageBox,
                            QComboBox)
import mysql.connector
from mysql.connector import Error
import logging

class ProgramDialog(QDialog):
    def __init__(self, parent=None, program=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Program")
        self.layout = QVBoxLayout(self)
        self.program = program
        self.conn = parent.conn if parent else None

        self.form_layout = QFormLayout()
        self.program_code = QLineEdit(self)
        self.college_school = QComboBox(self)  # Changed to QComboBox
        self.program_name = QLineEdit(self)

        # Populate college schools combo box
        self.populate_college_schools()

        self.form_layout.addRow("Program Code:", self.program_code)
        self.form_layout.addRow("College School:", self.college_school)
        self.form_layout.addRow("Program Name:", self.program_name)

        self.layout.addLayout(self.form_layout)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)    
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)

        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

        if program:
            self.program_code.setText(program["Program Code"])
            self.program_name.setText(program["Program Name"])
            # Set combo box to the correct college school
            index = self.college_school.findText(program["College School"])
            if index >= 0:
                self.college_school.setCurrentIndex(index)

    def populate_college_schools(self):
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT college_code, college_name FROM colleges")
            colleges = cursor.fetchall()
            
            self.college_school.clear()
            for code, name in colleges:
                self.college_school.addItem(f"{code} - {name}", code)
                
        except Error as e:
            logging.error("Error loading colleges: %s", e)
            QMessageBox.critical(self, "Database Error", 
                               "Failed to load college list")

    def validate_and_accept(self):
        if not all([self.program_code.text(), self.college_school.currentData(), 
                   self.program_name.text()]):
            QMessageBox.warning(self, "Validation Error", 
                              "All fields are required!")
            return
            
        if self.validate_program_code():
            self.accept()

    def validate_program_code(self):
        if not self.conn:
            QMessageBox.critical(self, "Database Error", 
                               "No database connection available")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Check if program code already exists (for new entries)
            if not self.program:
                cursor.execute(
                    "SELECT program_code FROM programs WHERE program_code = %s",
                    (self.program_code.text(),)
                )
                if cursor.fetchone():
                    QMessageBox.warning(self, "Duplicate Code", 
                                      "Program Code already exists!")
                    return False
            
            return True
            
        except Error as e:
            logging.error("Database error during validation: %s", e)
            QMessageBox.critical(self, "Database Error", 
                               f"Error validating program: {e}")
            return False

    def get_program_data(self):
        return {
            "program_code": self.program_code.text(),
            "college_school": self.college_school.currentData(),  # Returns the college code
            "program_name": self.program_name.text(),
        }