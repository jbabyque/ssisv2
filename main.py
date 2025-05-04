import sys
import logging
import csv
import mysql.connector

from mysql.connector import Error
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QListWidgetItem, QWidget, QGridLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QLineEdit, QComboBox, QHeaderView, QDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont

from ssishoncada_ui import Ui_MainWindow
from studentDialog import StudentDialog
from programDialog import ProgramDialog
from collegeDialog import CollegeDialog

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

STUDENT_FIELD_MAP = {
    "ID Number": "id_number",
    "Last Name": "last_name",
    "First Name": "first_name",
    "Middle Name": "middle_name",
    "Gender": "gender",
    "Year Level": "year_level",
    "Program Code": "program_code",
    "College Code": "college_code"
}

PROGRAM_FIELD_MAP = {
    "Program Code": "program_code",
    "College School": "college_school",
    "Program Name": "program_name"
}

COLLEGE_FIELD_MAP = {
    "College Code": "college_code",
    "College Name": "college_name"
}

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='ssisv2',
                user='root',  # Replace with your MySQL username
                password='Iloveyoubblouise<33'  # Replace with your MySQL password
            )
            logging.info("Connected to the database successfully")
            return self.connection
        except Error as e:
            logging.error("Error connecting to MySQL: %s", e)
            QMessageBox.critical(None, "Database Error", f"Failed to connect to database: {e}")
            return None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            
class MainWindow(QMainWindow):
    STUDENT_CSV = 'students.csv'
    PROGRAM_CSV = 'programs.csv'
    COLLEGE_CSV = 'colleges.csv'

    STUDENT_HEADERS = ["ID Number", "Last Name", "First Name", "Middle Name", "Gender", "Year Level", "Program Code", "College Code"]
    PROGRAM_HEADERS = ["Program Code", "College School", "Program Name"]
    COLLEGE_HEADERS = ["College Code", "College Name"]

    def __init__(self):
        super().__init__()

        try:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            
            self.titleLabel = self.ui.titleLabel 
            self.titleLabel.setText("S.S.I.S")
            
            self.titleIcon = self.ui.titleIcon
            self.titleIcon.hide()
            
            self.side_menu = self.ui.listWidget
            self.side_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.side_menu_iconOnly = self.ui.iconOnly
            self.side_menu_iconOnly.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            
            self.menu_button = self.ui.pushButton
            self.menu_button.setObjectName("")
            
            self.menu_button.setText("")
            self.menu_button.setIcon(QIcon("menu.svg"))
            self.menu_button.setIconSize(QSize(20,20))
            self.menu_button.setCheckable(True)
            self.menu_button.setChecked(False)
            self.main_content = self.ui.stackedWidget
            
            self.menu_list = [
                {
                    "name": "Student",
                    "icon": "./icons/user.svg"
                },
                {
                    "name": "Program",
                    "icon": "./icons/database.svg"
                },
                {
                    "name": "College",
                    "icon": "./icons/home.svg"
                },
            ]

            self.__init_signal_slot()
            self.init_list_widget()
            self.init_stackwidget()
            self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
            self.load_data_from_db("programs", self.program_table, self.PROGRAM_HEADERS)
            self.load_data_from_db("colleges", self.college_table, self.COLLEGE_HEADERS)
        except Exception as e:
            logging.error("Error initializing MainWindow: %s", e)
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            self.close()

    def __init_signal_slot(self):
        self.menu_button.toggled["bool"].connect(self.side_menu.setHidden)
        self.menu_button.toggled["bool"].connect(self.titleLabel.setHidden)
        self.menu_button.toggled["bool"].connect(self.side_menu.setHidden)
        self.menu_button.toggled["bool"].connect(self.side_menu_iconOnly.setVisible)
        
        self.side_menu.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu_iconOnly.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu.currentRowChanged['int'].connect(self.side_menu_iconOnly.setCurrentRow)
        self.side_menu_iconOnly.currentRowChanged['int'].connect(self.side_menu.setCurrentRow)
        self.menu_button.toggled.connect(self.button_icon_change)

    def init_list_widget(self):
        self.side_menu_iconOnly.clear()
        self.side_menu.clear()

        for menu in self.menu_list:
            item = QListWidgetItem()
            item.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            self.side_menu_iconOnly.addItem(item)
            self.side_menu_iconOnly.setCurrentRow(0)

            item_new = QListWidgetItem()
            item_new.setIcon(QIcon(menu.get("icon")))
            item_new.setText(menu.get("name"))
            self.side_menu.addItem(item_new)
            self.side_menu.setCurrentRow(0)

    def init_stackwidget(self):
        widget_list = self.main_content.findChildren(QWidget)
        for widget in widget_list:
            self.main_content.removeWidget(widget)

        for menu in self.menu_list:
            text = menu.get("name")

            if text == "Student":
                new_page = self.create_student_page()
            elif text == "Program":
                new_page = self.create_program_page()
            elif text == "College":
                new_page = self.create_college_page()
            else:
                layout = QGridLayout()
                label = QLabel(text)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                font = QFont()
                font.setPixelSize(20)
                label.setFont(font)
                layout.addWidget(label)
                new_page = QWidget()
                new_page.setLayout(layout)

            self.main_content.addWidget(new_page)

    def create_student_page(self):
        layout = QVBoxLayout()
        
        label = QLabel("Student Information")
        font = QFont("Century Gothic")
        font.setBold(True)
        font.setPixelSize(18)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        search_sort_layout = QHBoxLayout()
        
        search_label = QLabel("Search by:")
        self.student_search_combo = QComboBox()
        self.student_search_combo.addItems(self.STUDENT_HEADERS)
        self.student_search_input = QLineEdit()
        self.student_search_input.setPlaceholderText("Enter search term")
        self.student_search_input.textChanged.connect(self.search_student)
        search_sort_layout.addWidget(search_label)
        search_sort_layout.addWidget(self.student_search_combo)
        search_sort_layout.addWidget(self.student_search_input)

        sort_label = QLabel("Sort by:")
        self.student_sort_combo = QComboBox()
        self.student_sort_combo.addItems(self.STUDENT_HEADERS)
        self.student_sort_combo.currentIndexChanged.connect(self.sort_student)
        search_sort_layout.addWidget(sort_label)
        search_sort_layout.addWidget(self.student_sort_combo)

        layout.addLayout(search_sort_layout)

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(8)
        self.student_table.setHorizontalHeaderLabels(self.STUDENT_HEADERS)
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.student_table)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.setFixedSize(100, 30)
        add_button.clicked.connect(self.add_student)
        edit_button = QPushButton("Edit")
        edit_button.setFixedSize(100, 30)
        edit_button.clicked.connect(self.edit_student)
        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(100, 30)
        delete_button.clicked.connect(self.delete_student)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        page = QWidget()
        page.setLayout(layout)

        return page

    def create_program_page(self):
        layout = QVBoxLayout()
        
        label = QLabel("Program Information")
        font = QFont("Century Gothic")
        font.setBold(True)
        font.setPixelSize(18)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        search_sort_layout = QHBoxLayout()
        
        search_label = QLabel("Search by:")
        self.program_search_combo = QComboBox()
        self.program_search_combo.addItems(self.PROGRAM_HEADERS)
        self.program_search_input = QLineEdit()
        self.program_search_input.setPlaceholderText("Enter search term")
        self.program_search_input.textChanged.connect(self.search_program)
        search_sort_layout.addWidget(search_label)
        search_sort_layout.addWidget(self.program_search_combo)
        search_sort_layout.addWidget(self.program_search_input)

        sort_label = QLabel("Sort by:")
        self.program_sort_combo = QComboBox()
        self.program_sort_combo.addItems(self.PROGRAM_HEADERS)
        self.program_sort_combo.currentIndexChanged.connect(self.sort_program)
        search_sort_layout.addWidget(sort_label)
        search_sort_layout.addWidget(self.program_sort_combo)

        layout.addLayout(search_sort_layout)

        self.program_table = QTableWidget()
        self.program_table.setColumnCount(3)  
        self.program_table.setHorizontalHeaderLabels(self.PROGRAM_HEADERS)
        self.program_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.program_table)

        program_name_col_index = self.PROGRAM_HEADERS.index("Program Name")
        self.program_table.setColumnWidth(program_name_col_index, 250)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.setFixedSize(100, 30)
        add_button.clicked.connect(self.add_program)
        edit_button = QPushButton("Edit")
        edit_button.setFixedSize(100, 30)
        edit_button.clicked.connect(self.edit_program)
        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(100, 30)
        delete_button.clicked.connect(self.delete_program)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        page = QWidget()
        page.setLayout(layout)

        return page

    def create_college_page(self):
        layout = QVBoxLayout()
        
        label = QLabel("College Information")
        font = QFont("Century Gothic")
        font.setBold(True)
        font.setPixelSize(18)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        search_sort_layout = QHBoxLayout()
        
        search_label = QLabel("Search by:")
        self.college_search_combo = QComboBox()
        self.college_search_combo.addItems(self.COLLEGE_HEADERS)
        self.college_search_input = QLineEdit()
        self.college_search_input.setPlaceholderText("Enter search term")
        self.college_search_input.textChanged.connect(self.search_college)
        search_sort_layout.addWidget(search_label)
        search_sort_layout.addWidget(self.college_search_combo)
        search_sort_layout.addWidget(self.college_search_input)

        sort_label = QLabel("Sort by:")
        self.college_sort_combo = QComboBox()
        self.college_sort_combo.addItems(self.COLLEGE_HEADERS)
        self.college_sort_combo.currentIndexChanged.connect(self.sort_college)
        search_sort_layout.addWidget(sort_label)
        search_sort_layout.addWidget(self.college_sort_combo)

        layout.addLayout(search_sort_layout)

        self.college_table = QTableWidget()
        self.college_table.setColumnCount(2)
        self.college_table.setHorizontalHeaderLabels(self.COLLEGE_HEADERS)
        self.college_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.college_table)
        
        college_name_col_index = self.COLLEGE_HEADERS.index("College Name")
        self.college_table.setColumnWidth(college_name_col_index, 250)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.setFixedSize(100, 30)
        add_button.clicked.connect(self.add_college)
        edit_button = QPushButton("Edit")
        edit_button.setFixedSize(100, 30)
        edit_button.clicked.connect(self.edit_college)
        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(100, 30)
        delete_button.clicked.connect(self.delete_college)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        page = QWidget()
        page.setLayout(layout)

        return page
    
    def add_student(self):
        logging.debug("Opening StudentDialog")
        dialog = StudentDialog(self)
        dialog.conn = self.db_connection  # Pass the database connection
        logging.debug("StudentDialog initialized")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            logging.debug("StudentDialog accepted")
            student_data = dialog.get_student_data()
            logging.debug(f"Student data: {student_data}")
            if student_data:
                logging.debug(f"Student data received: {student_data}")
                if not all(student_data.values()):
                    QMessageBox.warning(self, "Invalid Data", "Please fill out all fields.")
                    return
                try:
                    db = DatabaseConnection()
                    connection = db.connect()
                    if connection:
                        cursor = connection.cursor()
                        query = """
                            INSERT INTO students (id_number, last_name, first_name, middle_name, 
                                                gender, year_level, program_code, college_code)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (
                            student_data['id_number'], 
                            student_data['last_name'], 
                            student_data['first_name'],
                            student_data['middle_name'], 
                            student_data['gender'], 
                            student_data['year_level'],
                            student_data['program_code'], 
                            student_data['college_code']
                        )
                        logging.debug(f"Executing query: {query} with values: {values}")
                        cursor.execute(query, values)
                        connection.commit()
                        cursor.close()
                        db.close()
                        logging.info("Student added successfully")
                        self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
                except Error as e:
                    logging.error("Error adding student to database: %s", e)
                    QMessageBox.critical(self, "Database Error", f"Failed to add student: {e}")

    def edit_student(self):
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            original_id = self.student_table.item(selected_row, 0).text()
            student_data = {
                "ID Number": original_id,
                "Last Name": self.student_table.item(selected_row, 1).text(),
                "First Name": self.student_table.item(selected_row, 2).text(),
                "Middle Name": self.student_table.item(selected_row, 3).text(),
                "Gender": self.student_table.item(selected_row, 4).text(),
                "Year Level": self.student_table.item(selected_row, 5).text(),
                "Program Code": self.student_table.item(selected_row, 6).text(),
                "College Code": self.student_table.item(selected_row, 7).text()
            }
            dialog = StudentDialog(self, student_data)
            if dialog.exec() == StudentDialog.DialogCode.Accepted:
                new_student_data = dialog.get_student_data()
                try:
                    db = DatabaseConnection()
                    connection = db.connect()
                    if connection:
                        cursor = connection.cursor()
                        query = """
                            UPDATE students 
                            SET id_number = %s, last_name = %s, first_name = %s, middle_name = %s,
                                gender = %s, year_level = %s, program_code = %s, college_code = %s
                            WHERE id_number = %s
                        """
                        values = (
                            new_student_data['id_number'],
                            new_student_data['last_name'],
                            new_student_data['first_name'],
                            new_student_data['middle_name'],
                            new_student_data['gender'],
                            new_student_data['year_level'],
                            new_student_data['program_code'],
                            new_student_data['college_code'],
                            original_id  # For WHERE clause
                        )
                        cursor.execute(query, values)
                        connection.commit()
                        cursor.close()
                        db.close()
                        self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
                except Error as e:
                    logging.error("Error updating student in database: %s", e)
                    QMessageBox.critical(self, "Database Error", f"Failed to update student: {e}")

    def delete_student(self):
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            student_id = self.student_table.item(selected_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete student {student_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
                
            try:
                db = DatabaseConnection()
                connection = db.connect()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "DELETE FROM students WHERE id_number = %s",
                        (student_id,)
                    )
                    connection.commit()
                    cursor.close()
                    db.close()
                    self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
            except Error as e:
                logging.error("Error deleting student from database: %s", e)
                QMessageBox.critical(self, "Database Error", f"Failed to delete student: {e}")

    def add_program(self):
        dialog = ProgramDialog(self)
        if dialog.exec() == ProgramDialog.DialogCode.Accepted:
            program_data = dialog.get_program_data()
            if not all(program_data.values()):
                QMessageBox.warning(self, "Invalid Data", "Please fill out all fields.")
                return
            try:
                db = DatabaseConnection()
                connection = db.connect()
                if connection:
                    cursor = connection.cursor()
                    query = """
                        INSERT INTO programs (program_code, college_school, program_name)
                        VALUES (%s, %s, %s)
                    """
                    values = (
                        program_data['program_code'],
                        program_data['college_school'],
                        program_data['program_name']
                    )
                    cursor.execute(query, values)
                    connection.commit()
                    cursor.close()
                    db.close()
                    self.load_data_from_db("programs", self.program_table, self.PROGRAM_HEADERS)
            except Error as e:
                logging.error("Error adding program to database: %s", e)
                QMessageBox.critical(self, "Database Error", f"Failed to add program: %e")

    def edit_program(self):
        selected_row = self.program_table.currentRow()
        if selected_row >= 0:
            program_data = {
                "Program Code": self.program_table.item(selected_row, 0).text(),
                "College School": self.program_table.item(selected_row, 1).text(),
                "Program Name": self.program_table.item(selected_row, 2).text()
            }
            dialog = ProgramDialog(self, program_data)
            if dialog.exec() == ProgramDialog.DialogCode.Accepted:
                new_program_data = dialog.get_program_data()
                try:
                    db = DatabaseConnection()
                    connection = db.connect()
                    if connection:
                        cursor = connection.cursor()
                        query = """
                            UPDATE programs 
                            SET program_code = %s, college_school = %s, program_name = %s
                            WHERE program_code = %s
                        """
                        values = (
                            new_program_data['program_code'],
                            new_program_data['college_school'],
                            new_program_data['program_name'],
                            program_data['Program Code']  # Original program code for WHERE clause
                        )
                        cursor.execute(query, values)
                        connection.commit()
                        cursor.close()
                        db.close()
                        self.load_data_from_db("programs", self.program_table, self.PROGRAM_HEADERS)
                except Error as e:
                    logging.error("Error updating program in database: %s", e)
                    QMessageBox.critical(self, "Database Error", f"Failed to update program: %e")

    def delete_program(self):
        selected_row = self.program_table.currentRow()
        if selected_row >= 0:
            program_code = self.program_table.item(selected_row, 0).text()
            
            # Check if there are students enrolled in this program
            try:
                db = DatabaseConnection()
                connection = db.connect()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM students WHERE program_code = %s",
                        (program_code,)
                    )
                    student_count = cursor.fetchone()[0]
                    
                    if student_count > 0:
                        reply = QMessageBox.question(
                            self, "Confirm Deletion",
                            f"This program has {student_count} enrolled student(s). Deleting it will set their Program Code to null. Proceed?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            return
                    
                    # Delete the program
                    cursor.execute(
                        "DELETE FROM programs WHERE program_code = %s",
                        (program_code,)
                    )
                    
                    # Update students with this program code to null
                    if student_count > 0:
                        cursor.execute(
                            "UPDATE students SET program_code = NULL WHERE program_code = %s",
                            (program_code,)
                        )
                    
                    connection.commit()
                    cursor.close()
                    db.close()
                    self.load_data_from_db("programs", self.program_table, self.PROGRAM_HEADERS)
                    # Also refresh students table if we updated any
                    if student_count > 0:
                        self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
            except Error as e:
                logging.error("Error deleting program from database: %s", e)
                QMessageBox.critical(self, "Database Error", f"Failed to delete program: %e")

    def add_college(self):
        try:
            dialog = CollegeDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                college_data = dialog.get_college_data()
                if not self.validate_college_data(college_data):
                    QMessageBox.warning(self, "Invalid Data", "Please fill out all fields.")
                    return
                
                try:
                    db = DatabaseConnection()
                    connection = db.connect()
                    if connection:
                        cursor = connection.cursor()
                        query = """
                            INSERT INTO colleges (college_code, college_name)
                            VALUES (%s, %s)
                        """
                        values = (
                            college_data['college_code'],
                            college_data['college_name']
                        )
                        cursor.execute(query, values)
                        connection.commit()
                        cursor.close()
                        db.close()
                        self.load_data_from_db("colleges", self.college_table, self.COLLEGE_HEADERS)
                except Error as e:
                    logging.error("Error adding college to database: %s", e)
                    QMessageBox.critical(self, "Database Error", f"Failed to add college: %e")
        except Exception as e:
            logging.error("Error adding college: %s", e)
            QMessageBox.critical(self, "Error", f"An error occurred while adding the college: %e")

    def edit_college(self):
        try:
            selected_row = self.college_table.currentRow()
            if selected_row >= 0:
                original_code = self.college_table.item(selected_row, 0).text()
                college_data = {
                    "College Code": original_code,
                    "College Name": self.college_table.item(selected_row, 1).text()
                }
                dialog = CollegeDialog(self, college=college_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_college_data = dialog.get_college_data()
                    if not self.validate_college_data(new_college_data):
                        QMessageBox.warning(self, "Invalid Data", "Please fill out all fields.")
                        return
                    
                    try:
                        db = DatabaseConnection()
                        connection = db.connect()
                        if connection:
                            cursor = connection.cursor()
                            # Update college
                            query = """
                                UPDATE colleges 
                                SET college_code = %s, college_name = %s
                                WHERE college_code = %s
                            """
                            values = (
                                new_college_data['college_code'],
                                new_college_data['college_name'],
                                original_code
                            )
                            cursor.execute(query, values)
                            
                            # If college code changed, update references in other tables
                            if new_college_data['college_code'] != original_code:
                                # Update programs
                                cursor.execute(
                                    "UPDATE programs SET college_school = %s WHERE college_school = %s",
                                    (new_college_data['college_code'], original_code)
                                )
                                # Update students
                                cursor.execute(
                                    "UPDATE students SET college_code = %s WHERE college_code = %s",
                                    (new_college_data['college_code'], original_code)
                                )
                            
                            connection.commit()
                            cursor.close()
                            db.close()
                            self.load_data_from_db("colleges", self.college_table, self.COLLEGE_HEADERS)
                            # Refresh other tables if college code changed
                            if new_college_data['college_code'] != original_code:
                                self.load_data_from_db("programs", self.program_table, self.PROGRAM_HEADERS)
                                self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
                    except Error as e:
                        logging.error("Error updating college in database: %s", e)
                        QMessageBox.critical(self, "Database Error", f"Failed to update college: %e")
        except Exception as e:
            logging.error("Error editing college: %s", e)
            QMessageBox.critical(self, "Error", f"An error occurred while editing the college: %e")

    def delete_college(self):
        selected_row = self.college_table.currentRow()
        if selected_row >= 0:
            college_code = self.college_table.item(selected_row, 0).text()

            # Check for dependencies
            try:
                db = DatabaseConnection()
                connection = db.connect()
                if connection:
                    cursor = connection.cursor()
                    
                    # Check for programs in this college
                    cursor.execute(
                        "SELECT COUNT(*) FROM programs WHERE college_school = %s",
                        (college_code,)
                    )
                    program_count = cursor.fetchone()[0]
                    
                    # Check for students in this college
                    cursor.execute(
                        "SELECT COUNT(*) FROM students WHERE college_code = %s",
                        (college_code,)
                    )
                    student_count = cursor.fetchone()[0]
                    
                    if program_count > 0 or student_count > 0:
                        reply = QMessageBox.question(
                            self, "Confirm Deletion",
                            f"This college has {program_count} program(s) and {student_count} student(s). "
                            "Deleting it will set their College references to null. Proceed?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            return
                    
                    # Delete the college
                    cursor.execute(
                        "DELETE FROM colleges WHERE college_code = %s",
                        (college_code,)
                    )
                    
                    # Update references in other tables
                    if program_count > 0:
                        cursor.execute(
                            "UPDATE programs SET college_school = NULL WHERE college_school = %s",
                            (college_code,)
                        )
                    
                    if student_count > 0:
                        cursor.execute(
                            "UPDATE students SET college_code = NULL, program_code = NULL WHERE college_code = %s",
                            (college_code,)
                        )
                    
                    connection.commit()
                    cursor.close()
                    db.close()
                    
                    # Refresh all tables
                    self.load_data_from_db("colleges", self.college_table, self.COLLEGE_HEADERS)
                    if program_count > 0:
                        self.load_data_from_db("programs", self.program_table, self.PROGRAM_HEADERS)
                    if student_count > 0:
                        self.load_data_from_db("students", self.student_table, self.STUDENT_HEADERS)
                    
                    logging.info(f"College '{college_code}' deleted and references updated")
                    
            except Error as e:
                logging.error("Error deleting college from database: %s", e)
                QMessageBox.critical(self, "Database Error", f"Failed to delete college: %e")

    def validate_college_data(self, college_data):
        return all(college_data.values())

    def button_icon_change(self, status):
        if status:
            self.menu_button.setIcon(QIcon("./icon/open.svg"))
        else:
            self.menu_button.setIcon(QIcon("./icon/close.svg"))

    def load_data_from_csv(self, file_path, table_widget, headers, field_map):
        try:
            with open(file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                table_widget.setRowCount(0)
                for row in reader:
                    row_position = table_widget.rowCount()
                    table_widget.insertRow(row_position)
                    for col, header in enumerate(headers):
                        field = field_map[header]
                        table_widget.setItem(row_position, col, QTableWidgetItem(row[field]))
        except FileNotFoundError:
            pass

    def save_data_to_csv(self, file_path, table_widget, headers, field_map):
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=field_map.values())
                writer.writeheader()
                for row in range(table_widget.rowCount()):
                    row_data = {field_map[header]: table_widget.item(row, col).text() for col, header in enumerate(headers)}
                    writer.writerow(row_data)
            logging.info(f"Data successfully saved to {file_path}")
        except Exception as e:
            logging.error(f"Error saving data to {file_path}: %s", e)
            QMessageBox.critical(self, "Error", f"An error occurred while saving data: %e")
                
    def search_student(self):
        search_term = self.student_search_input.text().lower()
        search_column = self.student_search_combo.currentIndex()
        for row in range(self.student_table.rowCount()):
            item = self.student_table.item(row, search_column)
            match = search_term in item.text().lower()
            self.student_table.setRowHidden(row, not match)

    def sort_student(self):
        column = self.student_sort_combo.currentIndex()
        self.student_table.sortItems(column)

    def search_program(self):
        search_term = self.program_search_input.text().lower()
        search_column = self.program_search_combo.currentIndex()
        for row in range(self.program_table.rowCount()):
            item = self.program_table.item(row, search_column)
            match = search_term in item.text().lower()
            self.program_table.setRowHidden(row, not match)

    def sort_program(self):
        column = self.program_sort_combo.currentIndex()
        self.program_table.sortItems(column)

    def search_college(self):
        search_term = self.college_search_input.text().lower()
        for row in range(self.college_table.rowCount()):
            match = False
            for col in range(self.college_table.columnCount()):
                item = self.college_table.item(row, col)
                if search_term in item.text().lower():
                    match = True
                    break
            self.college_table.setRowHidden(row, not match)

    def sort_college(self):
        column = self.college_sort_combo.currentIndex()
        self.college_table.sortItems(column)

    def load_data_from_db(self, table_name, table_widget, headers):
        try:
            db = DatabaseConnection()
            connection = db.connect()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                table_widget.setRowCount(0)
                for row in rows:
                    row_position = table_widget.rowCount()
                    table_widget.insertRow(row_position)
                    for col, header in enumerate(headers):
                        table_widget.setItem(row_position, col, QTableWidgetItem(str(row[header.lower()])))
                cursor.close()
                db.close()
        except Error as e:
            logging.error("Error loading data from database: %s", e)
            QMessageBox.critical(self, "Database Error", f"Failed to load data: %e")

    def save_data_to_db(self, table_name, table_widget, headers):
        try:
            db = DatabaseConnection()
            connection = db.connect()
            if connection:
                cursor = connection.cursor()
                cursor.execute(f"DELETE FROM {table_name}")  # Clear existing data
                for row in range(table_widget.rowCount()):
                    values = [table_widget.item(row, col).text() for col in range(table_widget.columnCount())]
                    placeholders = ', '.join(['%s'] * len(values))
                    query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                connection.commit() 
                cursor.close()
                db.close()
                logging.info(f"Data successfully saved to {table_name}")
        except Error as e:
            logging.error("Error saving data to database: %s", e)
            QMessageBox.critical(self, "Database Error", f"Failed to save data: %e")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    try:
        with open("style.qss") as f:
            style_str = f.read()
        app.setStyleSheet(style_str)
    except Exception as e:
        logging.error("Error loading stylesheet: %s", e)
        QMessageBox.critical(None, "Error", f"An error occurred loading the stylesheet: %e")

    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        logging.error("Error showing MainWindow: %s", e)
        QMessageBox.critical(None, "Error", f"An error occurred: %e")

    sys.exit(app.exec())
