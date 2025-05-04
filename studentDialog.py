from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFormLayout, QHBoxLayout, QComboBox,
                            QMessageBox)
import mysql.connector
from mysql.connector import Error
import logging

class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Student")
        self.layout = QVBoxLayout(self)
        self.student = student
        self.conn = parent.conn if parent else None

        self.form_layout = QFormLayout()
        self.id_number = QLineEdit(self)
        self.last_name = QLineEdit(self)
        self.first_name = QLineEdit(self)
        self.middle_name = QLineEdit(self)
        self.gender = QComboBox(self)
        self.gender.addItems(["Male", "Female", "Other"])
        self.year_level = QComboBox(self)
        self.year_level.addItems(["1", "2", "3", "4", "5"])
        
        # Changed to QComboBox for better user experience
        self.program_code = QComboBox(self)
        self.college_code = QComboBox(self)

        # Populate program and college combo boxes
        self.populate_programs()
        self.populate_colleges()

        self.form_layout.addRow("ID Number:", self.id_number)
        self.form_layout.addRow("Last Name:", self.last_name)
        self.form_layout.addRow("First Name:", self.first_name)
        self.form_layout.addRow("Middle Name:", self.middle_name)
        self.form_layout.addRow("Gender:", self.gender)
        self.form_layout.addRow("Year Level:", self.year_level)
        self.form_layout.addRow("Program Code:", self.program_code)
        self.form_layout.addRow("College Code:", self.college_code)

        self.layout.addLayout(self.form_layout)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)

        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

        if student:
            self.id_number.setText(student["ID Number"])
            self.last_name.setText(student["Last Name"])
            self.first_name.setText(student["First Name"])
            self.middle_name.setText(student["Middle Name"])
            self.gender.setCurrentText(student["Gender"])
            self.year_level.setCurrentText(student["Year Level"])
            
            # Set program and college combo boxes
            program_index = self.program_code.findData(student["Program Code"])
            if program_index >= 0:
                self.program_code.setCurrentIndex(program_index)
                
            college_index = self.college_code.findData(student["College Code"])
            if college_index >= 0:
                self.college_code.setCurrentIndex(college_index)

    def populate_programs(self):
        if not self.conn or not self.conn.is_connected():
            QMessageBox.critical(self, "Database Error", "No valid database connection available")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT program_code, program_name FROM programs")
            programs = cursor.fetchall()
            self.program_code.clear()
            for code, name in programs:
                self.program_code.addItem(f"{code} - {name}", code)
        except Error as e:
            logging.error("Error loading programs: %s", e)
            QMessageBox.critical(self, "Database Error", "Failed to load program list")

    def populate_colleges(self):
        if not self.conn or not self.conn.is_connected():
            QMessageBox.critical(self, "Database Error", "No valid database connection available")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT college_code, college_name FROM colleges")
            colleges = cursor.fetchall()
            
            self.college_code.clear()
            for code, name in colleges:
                self.college_code.addItem(f"{code} - {name}", code)
                
        except Error as e:
            logging.error("Error loading colleges: %s", e)
            QMessageBox.critical(self, "Database Error", 
                               "Failed to load college list")

    def validate_and_accept(self):
        required_fields = [
            self.id_number.text(),
            self.last_name.text(),
            self.first_name.text(),
            self.gender.currentText(),
            self.year_level.currentText(),
            self.program_code.currentData(),
            self.college_code.currentData()
        ]
        
        if not all(required_fields):
            QMessageBox.warning(self, "Validation Error", 
                              "All fields except Middle Name are required!")
            return
            
        if self.program_code.count() == 0 or self.college_code.count() == 0:
            QMessageBox.warning(self, "Validation Error", "Program and College must be selected!")
            return
            
        if self.validate_student_id():
            self.accept()

    def validate_student_id(self):
        if not self.conn:
            QMessageBox.critical(self, "Database Error", 
                               "No database connection available")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Check if student ID already exists (for new entries)
            if not self.student:
                cursor.execute(
                    "SELECT id_number FROM students WHERE id_number = %s",
                    (self.id_number.text(),)
                )
                if cursor.fetchone():
                    QMessageBox.warning(self, "Duplicate ID", 
                                      "Student ID already exists!")
                    return False
            
            return True
            
        except Error as e:
            logging.error("Database error during validation: %s", e)
            QMessageBox.critical(self, "Database Error", 
                               f"Error validating student: {e}")
            return False

    def get_student_data(self):
        try:
            return {
                "id_number": self.id_number.text(),
                "last_name": self.last_name.text(),
                "first_name": self.first_name.text(),
                "middle_name": self.middle_name.text(),
                "gender": self.gender.currentText(),
                "year_level": self.year_level.currentText(),
                "program_code": self.program_code.currentData(),
                "college_code": self.college_code.currentData()
            }
        except Exception as e:
            logging.error("Error retrieving student data: %s", e)
            QMessageBox.critical(self, "Error", "Failed to retrieve student data")
            return None

class SomeClass:
    def some_method(self):
        dialog = StudentDialog(self)

dialog = StudentDialog(self)
dialog.conn = self.db_connection  # Pass the database connection