from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from passlib.hash import pbkdf2_sha256
from functools import partial
import sqlite3
from PicButton import PicButton
import os
from ListWidgetImageItem import ListWidgetImageItem


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # ----------Load and add to stack pages below.--------------------------------------------------------------
        self.login_page = LoginPageUI(self)
        self.central_widget.addWidget(self.login_page)

        self.create_user_page = NewUserPageUI(self)
        self.central_widget.addWidget(self.create_user_page)

        self.menu_page = MenuPageUI(self)
        self.central_widget.addWidget(self.menu_page)

        self.admin_options_page = AdminOptionsPageUI(self)
        self.central_widget.addWidget(self.admin_options_page)

        self.create_menu_item_page = CreateMenuItemPageUI(self)
        self.central_widget.addWidget(self.create_menu_item_page)

        self.edit_menu_items_page = EditMenuItemsPageUI(self)
        self.central_widget.addWidget(self.edit_menu_items_page)

        self.edit_user_page = EditUserPageUI(self)
        self.central_widget.addWidget(self.edit_user_page)

        self.edit_bills_page = EditUserBillsPageUI(self)
        self.central_widget.addWidget(self.edit_bills_page)

        # ------------------Other stuff -----------------------------

        # Checks if the run_history table is empty, which should indicate a first run
        admins = conn.execute('''SELECT privileges FROM user_login WHERE privileges = 'a';''').fetchall()
        if len(admins) == 0:
            self.create_user_page.first_run()
            self.to_create_user_page()



    # --------------Page switch functions below.-----------------

    def to_login_page(self):
        self.login_page.userList.add_names()
        self.central_widget.setCurrentWidget(self.login_page)

    def to_create_user_page(self):
        self.central_widget.setCurrentWidget(self.create_user_page)

    def to_menu_page(self):
        self.central_widget.setCurrentWidget(self.menu_page)

    def to_admin_options_page(self):
        self.central_widget.setCurrentWidget(self.admin_options_page)

    def to_create_menu_item_page(self):
        self.central_widget.setCurrentWidget(self.create_menu_item_page)

    def to_edit_menu_items_page(self):
        self.central_widget.setCurrentWidget(self.edit_menu_items_page)

    def to_edit_user_page(self):
        self.central_widget.setCurrentWidget(self.edit_user_page)

    def to_edit_bills_page(self):
        self.central_widget.setCurrentWidget(self.edit_bills_page)

# ------------------Page defining classes below.-----------------


class LoginPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LoginPageUI, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.numpad = NumpadWidgetUI()
        self.userList = UserListWidgetUI()
        layout.addWidget(self.userList)
        layout.addWidget(self.numpad)
        self.setLayout(layout)

        self.numpad.pushButton_login.clicked.connect(self.login)
        self.numpad.lineEdit.setEchoMode(QLineEdit.Password)

    def login(self):
        selection = conn.execute('''SELECT ID, USERNAME, PWHASH, PRIVILEGES, BILL
                                    FROM USER_LOGIN INNER JOIN USER_BILLS ON USER_LOGIN.ID = USER_BILLS.USER_ID
                                    WHERE USERNAME = ?;''', (self.userList.listWidget.currentItem().text(),)).fetchone()
        if user_session.authenticate(selection, self.numpad.lineEdit.text()):
            print('authenticated')
            user_session.start_session(selection)
            window.menu_page.set_session_objects()
            window.to_menu_page()
            print('To menu page')
            self.clear_ui()

    def clear_ui(self):
        self.numpad.lineEdit.clear()


class NewUserPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NewUserPageUI, self).__init__(parent)

        self.create_user_form = CreateUserFormUI(self)
        self.virtual_keyboard = VirtualKeyboardUI(self)
        self.numpad = NumpadWidgetUI(self)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.create_user_form)
        self.stack.addWidget(self.virtual_keyboard)
        self.stack.addWidget(self.numpad)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.numpad.pushButton_login.setText('Enter')

        self.create_user_form.pushButton_keyboard.clicked.connect(self.show_keyboard)
        self.create_user_form.pushButton_numpad.clicked.connect(self.show_numpad)
        self.create_user_form.pushButton_createUser.clicked.connect(self.create_user_entry)
        self.numpad.pushButton_login.clicked.connect(self.numpad_enter)
        self.virtual_keyboard.pushButton_enter.clicked.connect(self.keyboard_enter)
        self.create_user_form.pushButton_back.clicked.connect(self.back)

    def show_keyboard(self):
        self.stack.setCurrentWidget(self.virtual_keyboard)

    def show_numpad(self):
        self.stack.setCurrentWidget(self.numpad)

    def show_form(self):
        self.stack.setCurrentWidget(self.create_user_form)

    def numpad_enter(self):
        self.create_user_form.lineEdit_pin.setText(self.numpad.lineEdit.text())
        self.numpad.lineEdit.clear()
        self.show_form()

    def keyboard_enter(self):
        self.create_user_form.lineEdit_username.setText(self.virtual_keyboard.lineEdit.text())
        self.virtual_keyboard.lineEdit.clear()
        self.show_form()

    def create_user_entry(self):
        try:
            if self.create_user_form.lineEdit_username.text() != '':
                if self.create_user_form.checkBox_admin.isChecked():
                    privileges = 'a'
                else:
                    privileges = 'b'
                if len(self.create_user_form.lineEdit_pin.text()) == 4:
                    pwhash = pbkdf2_sha256.hash(self.create_user_form.lineEdit_pin.text())
                    conn.execute("INSERT INTO USER_LOGIN (USERNAME, PWHASH, PRIVILEGES) \
                                  VALUES (?,?,?);",
                                 (self.create_user_form.lineEdit_username.text().strip(), pwhash, privileges))
                    conn.commit()
                    user_id = conn.execute("SELECT id "
                                           "FROM user_login "
                                           "WHERE username = ?;",
                                           (self.create_user_form.lineEdit_username.text(),)).fetchone()
                    conn.execute("INSERT INTO user_bills (user_id, bill) \
                                  VALUES (?, ?);", (user_id[0], 0.0,))
                    conn.commit()
                    window.to_admin_options_page()
                    window.login_page.userList.add_names()
                    window.edit_user_page.user_list.add_names()
                    self.clear_ui()
                else:
                    self.create_user_form.label_error.setText('Pin not 4 digits long')
            else:
                self.create_user_form.label_error.setText('Must enter username')
        except sqlite3.IntegrityError:
            self.create_user_form.label_error.setText('Username already in use')

    def write_edit(self, user_id):
        user_id = user_id
        try:
            if self.create_user_form.lineEdit_username.text() != '':
                if self.create_user_form.checkBox_admin.isChecked():
                    privileges = 'a'
                else:
                    privileges = 'b'
                if len(self.create_user_form.lineEdit_pin.text()) == 4:
                    pwhash = pbkdf2_sha256.hash(self.create_user_form.lineEdit_pin.text())
                    conn.execute("UPDATE user_login SET username = ?, pwhash = ?, privileges = ? WHERE id = ?;",
                                 (self.create_user_form.lineEdit_username.text().strip(), pwhash, privileges, user_id))
                    conn.commit()
                    window.to_admin_options_page()
                    self.create_mode()
                    self.clear_ui()
                    window.login_page.userList.add_names()
                    window.edit_user_page.user_list.add_names()
                else:
                    self.create_user_form.label_error.setText('Pin not 4 digits long')
            else:
                self.create_user_form.label_error.setText('Must enter username')
        except sqlite3.IntegrityError:
            self.create_user_form.label_error.setText('Username already in use')

    def clear_ui(self):
        self.create_user_form.label_firstRun.setText('')
        self.create_user_form.lineEdit_username.clear()
        self.create_user_form.lineEdit_pin.clear()
        self.create_user_form.checkBox_admin.setEnabled(True)
        self.create_user_form.checkBox_admin.setChecked(False)

    def edit_mode(self, selection):
        self.create_user_form.label_firstRun.setText('')
        id = selection[0]
        self.create_user_form.checkBox_admin.setEnabled(True)
        self.create_user_form.lineEdit_username.setText(selection[1])

        if selection[3] == 'a':
            self.create_user_form.checkBox_admin.setChecked(True)

        self.create_user_form.pushButton_createUser.disconnect()
        self.create_user_form.pushButton_createUser.clicked.connect(partial(self.write_edit, id))
        self.create_user_form.pushButton_createUser.setText('Update Profile')

    def create_mode(self):
        self.create_user_form.label_firstRun.setText('')
        self.create_user_form.checkBox_admin.setEnabled(True)
        self.create_user_form.pushButton_createUser.disconnect()
        self.create_user_form.pushButton_createUser.clicked.connect(self.create_user_entry)
        self.create_user_form.pushButton_createUser.setText('Create User')

    def first_run(self):
        self.create_user_form.label_firstRun.setText('Welcome. No admins yet, create admin account.')
        self.create_user_form.checkBox_admin.setChecked(True)
        self.create_user_form.checkBox_admin.setEnabled(False)
        self.create_user_form.pushButton_createUser.disconnect()
        self.create_user_form.pushButton_back.disconnect()
        self.create_user_form.pushButton_createUser.clicked.connect(self.write_first_admin)
        self.create_user_form.pushButton_createUser.setText('Create Admin')

    def write_first_admin(self):
        try:
            if self.create_user_form.lineEdit_username.text() != '':
                if self.create_user_form.checkBox_admin.isChecked():
                    privileges = 'a'
                else:
                    privileges = 'b'
                if len(self.create_user_form.lineEdit_pin.text()) == 4:
                    pwhash = pbkdf2_sha256.hash(self.create_user_form.lineEdit_pin.text())
                    conn.execute("INSERT INTO USER_LOGIN (USERNAME, PWHASH, PRIVILEGES) \
                                  VALUES (?,?,?);",
                                 (self.create_user_form.lineEdit_username.text().strip(), pwhash, privileges))
                    conn.commit()
                    user_id = conn.execute("SELECT id "
                                           "FROM user_login "
                                           "WHERE username = ?;",
                                           (self.create_user_form.lineEdit_username.text(),)).fetchone()
                    conn.execute("INSERT INTO user_bills (user_id, bill) \
                                  VALUES (?, ?);", (user_id[0], 0.0,))
                    conn.commit()
                    window.to_login_page()
                    window.login_page.userList.add_names()
                    window.edit_user_page.user_list.add_names()
                    self.create_mode()
                    self.clear_ui()
                else:
                    self.create_user_form.label_error.setText('Pin not 4 digits long')
            else:
                self.create_user_form.label_error.setText('Must enter username')
        except sqlite3.IntegrityError:
            self.create_user_form.label_error.setText('Username already in use')


    def back(self):
        window.to_admin_options_page()
        self.clear_ui()


class MenuPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MenuPageUI, self).__init__(parent)
        print('loading ui')
        loadUi('menu.ui', self)
        print('at menu page')
        # ------------------- handling menu button fields below --------------------------

        self.menu_stack = QtWidgets.QStackedWidget()

        self.drink_button_fields = QStackedWidget()
        self.menu_stack.addWidget(self.drink_button_fields)

        self.snack_button_fields = QStackedWidget()
        self.menu_stack.addWidget(self.snack_button_fields)

        self.food_button_fields = QStackedWidget()
        self.menu_stack.addWidget(self.food_button_fields)

        self.pay_bills_buttons = PayButtonsUI(self)
        self.menu_stack.addWidget(self.pay_bills_buttons)

        self.menu_stack.setCurrentWidget(self.food_button_fields)
        self.load_menu_buttons()

        self.pushButton_admin.clicked.connect(self.parent().to_admin_options_page)

        # ------------------- Menu page UI widgets handled below -----------------------------

        self.pushButton_drinks.clicked.connect(self.to_drinks_menu)
        self.pushButton_snacks.clicked.connect(self.to_snacks_menu)
        self.pushButton_food.clicked.connect(self.to_food_menu)
        self.pushButton_pay.clicked.connect(self.to_pay_menu)
        self.pushButton_clear.clicked.connect(self.clear_purchase)
        self.pushButton_purchase.clicked.connect(self.write_purchase)
        self.pushButton_logout.clicked.connect(self.logout)
        self.pushButton_admin.hide()

        # ----------------------------------------------------------------------------------
        self.purchase_total = 0
        self.row = 0
        self.previous_button = 'food'
        self.pushButton_food.setStyleSheet("background-color: #91b6f2")

        self.pay_bills_buttons.pushButton_1.clicked.connect(partial(self.button_click, '$1', -1))
        self.pay_bills_buttons.pushButton_5.clicked.connect(partial(self.button_click, '$5', -5))
        self.pay_bills_buttons.pushButton_10.clicked.connect(partial(self.button_click, '$10', -10))
        self.pay_bills_buttons.pushButton_20.clicked.connect(partial(self.button_click, '$20', -20))

    def set_session_objects(self):
        print('setting session objects')
        self.label_username.setText(user_session.username)
        print(user_session.username)

        if user_session.privileges == 'a':
            self.pushButton_admin.show()
        else:
            self.pushButton_admin.hide()

        if user_session.bill <= 0:
            self.label_billLabel.setText('Your credit:')
        else:
            self.label_billLabel.setText('You owe:')

        self.label_bill.setText('${:6.2f}'.format(abs(user_session.bill/100)))
        self.to_food_menu()
        self.food_button_fields.setCurrentIndex(0)
        self.pushButton_food.setText('Food (1)')

    def load_menu_buttons(self):
        # reinitializes these widgets associated with the menu stacks so they reflect changes appropriately
        self.food_button_fields = QStackedWidget()
        self.drink_button_fields = QStackedWidget()
        self.snack_button_fields = QStackedWidget()
        self.menu_stack.addWidget(self.food_button_fields)
        self.menu_stack.addWidget(self.snack_button_fields)
        self.menu_stack.addWidget(self.drink_button_fields)
        self.verticalLayout.addWidget(self.menu_stack)
        self.menu_stack.setCurrentWidget(self.food_button_fields)

        # ---------------Setting up type based stacks-----------------------------------

        self.food_buttons = []
        self.food_buttons.append(MenuButtonFieldUI(self))
        self.food_button_fields.addWidget(self.food_buttons[0])
        self.food_button_fields.setCurrentWidget(self.food_buttons[0])
        food_buttons_total = 0
        self.food_button_pages = 0

        self.snack_buttons = []
        self.snack_buttons.append(MenuButtonFieldUI(self))
        self.snack_button_fields.addWidget(self.snack_buttons[0])
        self.snack_button_fields.setCurrentWidget(self.snack_buttons[0])
        snack_buttons_total = 0
        self.snack_button_pages = 0

        self.drink_buttons = []
        self.drink_buttons.append(MenuButtonFieldUI(self))
        self.drink_button_fields.addWidget(self.drink_buttons[0])
        self.drink_button_fields.setCurrentWidget(self.drink_buttons[0])
        drink_buttons_total = 0
        self.drink_button_pages = 0

        # ---------------Procedural button creation based on database entries------------------------

        selection = conn.execute('SELECT item_name, price, category, icon_path FROM menu_items')
        self.buttons = []
        fc = 0
        fr = 0

        dc = 0
        dr = 0

        sc = 0
        sr = 0
        for item in selection:

            if item[2] == 'food':
                if food_buttons_total % 6 == 0 and food_buttons_total != 0:
                    self.food_buttons.append(MenuButtonFieldUI(self))  # adds a new holder for the new menu buttons
                    self.food_button_fields.addWidget(
                        self.food_buttons[-1])  # adds that holder to the stack of food buttons
                    self.food_button_pages += 1

                self.buttons.append(PicButton(QPixmap(item[3]),
                                              item[0],
                                              item[1]))
                self.buttons[-1].clicked.connect(partial(self.button_click, item[0], item[1]))
                self.food_buttons[self.food_button_pages].gridLayout.addWidget(self.buttons[-1], fr, fc)
                if fc < 2:
                    fc += 1
                else:
                    fc = 0
                    fr += 1
                food_buttons_total += 1

            if item[2] == 'snack':
                if snack_buttons_total % 6 == 0 and snack_buttons_total != 0:
                    self.snack_buttons.append(MenuButtonFieldUI(self))  # adds a new holder for the new menu buttons
                    self.snack_button_fields.addWidget(
                        self.snack_buttons[-1])  # adds that holder to the stack of food buttons
                    self.snack_button_pages += 1

                self.buttons.append(PicButton(QPixmap(item[3]),
                                              item[0],
                                              item[1]))
                self.buttons[-1].clicked.connect(partial(self.button_click, item[0], item[1]))
                self.snack_buttons[self.snack_button_pages].gridLayout.addWidget(self.buttons[-1], sr, sc)
                if sc < 2:
                    sc += 1
                else:
                    sc = 0
                    sr += 1
                    snack_buttons_total += 1

            if item[2] == 'drink':
                if drink_buttons_total % 6 == 0 and drink_buttons_total != 0:
                    self.drink_buttons.append(MenuButtonFieldUI(self))  # adds a new holder for the new menu buttons
                    self.drink_button_fields.addWidget(
                        self.drink_buttons[-1])  # adds that holder to the stack of food buttons
                    self.drink_button_pages += 1

                self.buttons.append(PicButton(QPixmap(item[3]),
                                              item[0],
                                              item[1]))
                self.buttons[-1].clicked.connect(partial(self.button_click, item[0], item[1]))
                self.drink_buttons[self.drink_button_pages].gridLayout.addWidget(self.buttons[-1], dr, dc)
                if dc < 2:
                    dc += 1
                else:
                    dc = 0
                    dr += 1
                    drink_buttons_total += 1

    def button_click(self, name, price):
        found_item = self.tableWidget.findItems(name, Qt.MatchExactly)
        if found_item == []:
            self.tableWidget.insertRow(self.row)
            self.tableWidget.setItem(self.row, 0, QTableWidgetItem(name))
            self.tableWidget.setItem(self.row, 1, QTableWidgetItem('1'))
            self.row += 1
        else:
            try:
                item_row = self.tableWidget.row(found_item[0])
                previous_quantity = int(self.tableWidget.item(item_row, 1).text())
                self.tableWidget.setItem(item_row, 1, QTableWidgetItem(str(previous_quantity + 1)))
            except IndexError as e:
                print(e)

        self.purchase_total += price*100
        self.label_total.setText('{:6.2f}'.format(self.purchase_total/100))

    def to_drinks_menu(self):
        self.menu_stack.setCurrentWidget(self.drink_button_fields)
        if self.previous_button != 'drinks':
            self.drink_button_fields.setCurrentIndex(0)
            self.previous_button = 'drinks'

        else:
            if self.drink_button_fields.currentIndex() == self.drink_button_pages \
                    or self.drink_button_fields.currentIndex() > self.drink_button_pages:
                self.drink_button_fields.setCurrentIndex(0)
            else:
                self.drink_button_fields.setCurrentIndex(self.drink_button_fields.currentIndex() + 1)

        self.pushButton_drinks.setText('Drinks (' + str(self.drink_button_fields.currentIndex() + 1) + ')')
        self.pushButton_food.setStyleSheet("")
        self.pushButton_snacks.setStyleSheet("")
        self.pushButton_pay.setStyleSheet("")
        self.pushButton_drinks.setStyleSheet("background-color: #91b6f2")
        self.snack_button_fields.setCurrentIndex(0)
        self.food_button_fields.setCurrentIndex(0)

    def to_food_menu(self):
        self.menu_stack.setCurrentWidget(self.food_button_fields)
        if self.previous_button != 'food':
            self.food_button_fields.setCurrentIndex(0)
            self.previous_button = 'food'

        else:
            if self.food_button_fields.currentIndex() == self.food_button_pages \
                    or self.food_button_fields.currentIndex() > self.food_button_pages:
                self.food_button_fields.setCurrentIndex(0)
            else:
                self.food_button_fields.setCurrentIndex(self.food_button_fields.currentIndex()+1)

        self.pushButton_food.setText('Food (' + str(self.food_button_fields.currentIndex() + 1) + ')')
        self.pushButton_drinks.setStyleSheet("")
        self.pushButton_snacks.setStyleSheet("")
        self.pushButton_pay.setStyleSheet("")
        self.pushButton_food.setStyleSheet("background-color: #91b6f2")
        self.drink_button_fields.setCurrentIndex(0)
        self.snack_button_fields.setCurrentIndex(0)

    def to_snacks_menu(self):
        self.menu_stack.setCurrentWidget(self.snack_button_fields)
        if self.previous_button != 'snacks':
            self.snack_button_fields.setCurrentIndex(0)
            self.previous_button = 'snacks'

        else:
            if self.snack_button_fields.currentIndex() == self.snack_button_pages \
                    or self.snack_button_fields.currentIndex() > self.snack_button_pages:
                self.snack_button_fields.setCurrentIndex(0)
            else:
                self.snack_button_fields.setCurrentIndex(self.snack_button_fields.currentIndex() + 1)

        self.pushButton_snacks.setText('Snacks (' + str(self.snack_button_fields.currentIndex() + 1) + ')')
        self.pushButton_food.setStyleSheet("")
        self.pushButton_drinks.setStyleSheet("")
        self.pushButton_pay.setStyleSheet("")
        self.pushButton_snacks.setStyleSheet("background-color: #91b6f2")
        self.drink_button_fields.setCurrentIndex(0)
        self.food_button_fields.setCurrentIndex(0)

    def to_pay_menu(self):
        self.previous_button = 'pay'
        self.menu_stack.setCurrentWidget(self.pay_bills_buttons)
        self.pushButton_drinks.setStyleSheet("")
        self.pushButton_food.setStyleSheet("")
        self.pushButton_snacks.setStyleSheet("")
        self.pushButton_pay.setStyleSheet("background-color: #91b6f2")
        self.drink_button_fields.setCurrentIndex(0)
        self.food_button_fields.setCurrentIndex(0)
        self.snack_button_fields.setCurrentIndex(0)

    def clear_purchase(self):
        self.purchase_total = 0
        # clear the table
        self.tableWidget.setRowCount(0)
        self.row = 0
        self.label_total.setText('0.00')

    def write_purchase(self):
        conn.execute('''UPDATE user_bills 
                        SET bill = ?
                        WHERE user_id = ?;''',
                     (self.purchase_total + user_session.bill, user_session.user_id))
        conn.commit()
        self.clear_purchase()
        user_session.end_session()
        window.to_login_page()

    def logout(self):
        self.clear_purchase()
        user_session.end_session()
        window.to_login_page()


class AdminOptionsPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AdminOptionsPageUI, self).__init__(parent)
        loadUi('admin_options.ui', self)

        self.pushButton_createNewUser.clicked.connect(self.parent().to_create_user_page)
        self.pushButton_back.clicked.connect(self.parent().to_menu_page)
        self.pushButton_addMenuItem.clicked.connect(self.parent().to_create_menu_item_page)
        self.pushButton_editMenuItems.clicked.connect(self.parent().to_edit_menu_items_page)
        self.pushButton_manageUserProfiles.clicked.connect(self.parent().to_edit_user_page)
        self.pushButton_manageUserBills.clicked.connect(self.to_manage_bills)
        self.pushButton_exitApplication.clicked.connect(app.quit)

    def to_manage_bills(self):
        window.edit_bills_page.load_table()
        window.to_edit_bills_page()


class CreateMenuItemPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CreateMenuItemPageUI, self).__init__(parent)

        self.create_menu_item_page = NewMenuItemFormUI(self)
        self.numpad = NumpadWidgetUI(self)
        self.numpad.set_money_mode()
        self.keyboard = VirtualKeyboardUI(self)

        self.stack = QtWidgets.QStackedWidget(self)
        self.stack.addWidget(self.create_menu_item_page)
        self.stack.addWidget(self.numpad)
        self.stack.addWidget(self.keyboard)
        self.stack.setCurrentWidget(self.create_menu_item_page)

        self.keyboard.pushButton_enter.clicked.connect(self.keyboard_enter)
        self.numpad.pushButton_login.clicked.connect(self.numpad_enter)

        self.load_icon_list()
        self.preview_button = PicButton(QPixmap(self.create_menu_item_page.listWidget.currentItem().value), '', 0)
        self.create_menu_item_page.verticalLayout.addWidget(self.preview_button)

        self.create_menu_item_page.lineEdit_name.textChanged.connect(self.update_preview)
        self.create_menu_item_page.lineEdit_price.textChanged.connect(self.update_preview)
        self.create_menu_item_page.listWidget.currentRowChanged.connect(self.update_preview)

        self.create_menu_item_page.pushButton_print.clicked.connect(self.done)
        self.create_menu_item_page.pushButton_keyboard.clicked.connect(self.show_keyboard)
        self.create_menu_item_page.pushButton_numpad.clicked.connect(self.show_numpad)
        self.create_menu_item_page.pushButton_back.clicked.connect(self.back)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def load_icon_list(self):
        for file in os.listdir(os.path.join(ROOT_DIR, 'button_icons')):
            if file.endswith('.png'):
                item = ListWidgetImageItem(os.path.join(os.curdir, 'button_icons', file),
                                           os.path.join(os.curdir, 'button_icons', file))
                self.create_menu_item_page.listWidget.addItem(item)

        self.create_menu_item_page.listWidget.setCurrentRow(0)

    def done(self):
        if (self.create_menu_item_page.lineEdit_name.text() != '' and
                self.create_menu_item_page.lineEdit_price.text() != ''):
            try:
                conn.execute("INSERT INTO menu_items (item_name, price, category, icon_path) \
                                                  VALUES (?,?,?,?);",
                             (self.create_menu_item_page.lineEdit_name.text(),
                              self.create_menu_item_page.lineEdit_price.text(),
                              self.create_menu_item_page.comboBox_type.currentText(),
                              self.create_menu_item_page.listWidget.currentItem().value))
                conn.commit()
                self.clear_ui()
                window.to_admin_options_page()
                window.menu_page.load_menu_buttons()
                window.edit_menu_items_page.load_table()
            except sqlite3.IntegrityError:
                self.create_menu_item_page.label_status.setText('Menu item already exists')
        else:
            self.create_menu_item_page.label_status.setText('Must enter price and name')

    def show_keyboard(self):
        self.stack.setCurrentWidget(self.keyboard)

    def show_numpad(self):
        self.stack.setCurrentWidget(self.numpad)

    def show_main(self):
        self.stack.setCurrentWidget(self.create_menu_item_page)

    def numpad_enter(self):
        self.create_menu_item_page.lineEdit_price.setText(self.numpad.lineEdit.text())
        self.numpad.lineEdit.clear()
        self.show_main()

    def keyboard_enter(self):
        self.create_menu_item_page.lineEdit_name.setText(self.keyboard.lineEdit.text())
        self.keyboard.lineEdit.clear()
        self.show_main()

    def clear_ui(self):
        self.create_menu_item_page.lineEdit_name.clear()
        self.create_menu_item_page.lineEdit_price.clear()
        self.create_menu_item_page.listWidget.setCurrentRow(0)


    def back(self):
        window.to_admin_options_page()
        self.clear_ui()

    def update_preview(self):
        self.preview_button.set_name(self.create_menu_item_page.lineEdit_name.text())
        self.preview_button.set_icon(QPixmap(self.create_menu_item_page.listWidget.currentItem().value))
        if self.create_menu_item_page.lineEdit_price.text() != '':
            self.preview_button.set_price(self.create_menu_item_page.lineEdit_price.text()) #this is causing problems

    def enter_edit_mode(self, selection):
        self.name = selection[0]
        price = selection[1]
        category = selection[2]
        icon_path = str(selection[3])
        self.id = selection[4]
        print(str(selection[3]))
        print('before connections')
        self.create_menu_item_page.pushButton_print.disconnect()
        self.create_menu_item_page.pushButton_print.clicked.connect(self.write_edit)
        print('after connections')
        self.create_menu_item_page.lineEdit_name.insert(self.name)
        self.create_menu_item_page.lineEdit_price.insert(str(price))
        print('after text setting')
        self.create_menu_item_page.comboBox_type.setCurrentIndex(
            self.create_menu_item_page.comboBox_type.findText(category))
        print('after combo box setting')

        for item in range(self.create_menu_item_page.listWidget.count()):
            if self.create_menu_item_page.listWidget.item(item).value == icon_path:
                self.create_menu_item_page.listWidget.setCurrentRow(item)

    def enter_create_mode(self):
        self.create_menu_item_page.pushButton_print.disconnect()
        self.create_menu_item_page.pushButton_print.clicked.connect(self.done)
        self.clear_ui()

    def write_edit(self):
        conn.execute("UPDATE menu_items SET item_name = ?, price = ?, category = ?, icon_path = ? WHERE id = ?;",
                     (self.create_menu_item_page.lineEdit_name.text(),
                      self.create_menu_item_page.lineEdit_price.text(),
                      self.create_menu_item_page.comboBox_type.currentText(),
                      self.create_menu_item_page.listWidget.currentItem().value,
                      self.id))
        conn.commit()
        print('pressed enter')
        self.clear_ui()
        window.to_edit_menu_items_page()
        window.menu_page.load_menu_buttons()
        window.edit_menu_items_page.load_table()
        self.enter_create_mode()


class EditMenuItemsPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EditMenuItemsPageUI, self).__init__(parent)
        loadUi('edit_item_table.ui', self)

        self.load_table()

        self.pushButton_edit.clicked.connect(self.edit)
        self.pushButton_delete.clicked.connect(self.delete_item)
        self.pushButton_back.clicked.connect(self.parent().to_admin_options_page)

    def load_table(self):
        selection = conn.execute('SELECT item_name, price FROM menu_items')
        row = 0
        self.tableWidget.setRowCount(0)
        for item in selection:
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(item[0]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(item[1])))
            row += 1

    def edit(self):
        selected_item = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        sel = conn.execute("SELECT item_name, price, category, icon_path, id \
                                        FROM menu_items \
                                        WHERE item_name = ?;", (selected_item,)).fetchone()
        window.create_menu_item_page.enter_edit_mode(sel)
        window.to_create_menu_item_page()

    def delete_item(self):
        selected_item = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        conn.execute('''DELETE FROM menu_items WHERE item_name = ?;''', (selected_item,))
        conn.commit()
        self.load_table()
        window.menu_page.load_menu_buttons()


class EditUserPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EditUserPageUI, self).__init__(parent)
        loadUi('edit_user_page.ui', self)

        self.user_list = UserListWidgetUI(self)
        self.verticalLayout.addWidget(self.user_list)
        self.pushButton_edit.clicked.connect(self.edit_user)
        self.pushButton_delete.clicked.connect(self.delete_user)
        self.pushButton_back.clicked.connect(self.back)

    def edit_user(self):
        try:
            selection = conn.execute('''SELECT ID, USERNAME, PWHASH, PRIVILEGES
                                                FROM USER_LOGIN
                                                WHERE USERNAME = ?;''',
                                     (self.user_list.listWidget.currentItem().text(),)).fetchone()
            window.create_user_page.edit_mode(selection)
            window.to_create_user_page()
            self.label_message.setText('')
        except Exception as e:
            print(e)

    def delete_user(self):
        try:
            selected_user = self.user_list.listWidget.currentItem().text()
            if selected_user == user_session.username:
                self.label_message.setText('You can\'t delete the account you\'re logged into dummy.')
            else:
                id = conn.execute('SELECT id FROM user_login WHERE username = ?;',
                                            (self.user_list.listWidget.currentItem().text(),)).fetchone()
                conn.execute('DELETE FROM user_login WHERE id = ?;',
                             (str(id[0]),))
                conn.execute('DELETE FROM user_bills WHERE user_id = ?;',
                             (str(id[0]),))
                conn.commit()
                self.label_message.setText('')
                self.user_list.add_names()
        except Exception as e:
            print(e)

    def back(self):
        self.label_message.setText('')
        window.to_admin_options_page()


class EditUserBillsPageUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EditUserBillsPageUI, self).__init__(parent)
        self.landing = EditBillsLandingUI(self)
        self.numpad = NumpadWidgetUI(self)
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.landing)
        self.stack.addWidget(self.numpad)
        self.stack.setCurrentWidget(self.landing)
        self.numpad.set_money_mode()
        self.load_table()

        self.landing.pushButton_edit.clicked.connect(self.edit_bill)
        self.landing.pushButton_charge.clicked.connect(self.charge_bill)
        self.landing.pushButton_credit.clicked.connect(self.credit_bill)
        self.landing.pushButton_back.clicked.connect(self.back)

        self.numpad.pushButton_login.disconnect()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def load_table(self):
        join_selection = conn.execute('''SELECT username, bill FROM USER_LOGIN  INNER JOIN user_bills 
                                        ON user_login.id = user_bills.user_id;''').fetchall()
        print(join_selection)
        row = 0
        self.landing.tableWidget.setRowCount(0)
        for item in join_selection:
            decimal_bill = float(item[1])/100
            self.landing.tableWidget.insertRow(row)
            self.landing.tableWidget.setItem(row, 0, QTableWidgetItem(item[0]))
            self.landing.tableWidget.setItem(row, 1, QTableWidgetItem('{:.2f}'.format(decimal_bill)))
            row += 1
            selection = conn.execute('''SELECT bill FROM user_bills;''')
            total_debt = 0
            for bill in selection:
                total_debt += bill[0]
            self.landing.label_debt.setText('${:6.2f}'.format(total_debt/100))

    def edit_bill(self):
        selected_bill = self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 1).text()
        if selected_bill is not None:
            print('editing bill')
            self.numpad.pushButton_login.clicked.connect(self.write_edit)
            self.numpad.lineEdit.setText(selected_bill)
            self.stack.setCurrentWidget(self.numpad)

    def credit_bill(self):
        if self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 1) is not None:
            print('Crediting bill')
            self.numpad.pushButton_login.clicked.connect(self.write_credit)
            self.stack.setCurrentWidget(self.numpad)

    def charge_bill(self):
        if self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 1) is not None:
            print('Charging bill')
            self.numpad.pushButton_login.clicked.connect(self.write_charge)
            self.stack.setCurrentWidget(self.numpad)

    def write_edit(self):
        username = self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 0).text()
        print(self.numpad.lineEdit.text())
        # Converting all money to cents with *100 for DB storage
        try:
            conn.execute('''UPDATE user_bills
                            SET bill = ?
                            WHERE user_id = (SELECT id FROM user_login 
                                             WHERE username = ?);''',
                         (int(float(self.numpad.lineEdit.text())*100), username))
            conn.commit()
            print(self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 0).text())
            self.numpad.lineEdit.clear()
            self.load_table()
            self.stack.setCurrentWidget(self.landing)
        except ValueError as e:
            print(e)

    def write_credit(self):
        try:
            selected_user = self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 0).text()
            selected_bill = self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 1).text()
            conn.execute('''UPDATE user_bills
                                    SET bill = ?
                                    WHERE user_id = (SELECT id FROM user_login 
                                                     WHERE username = ?);''',
                         (int(float(selected_bill) * 100) - int(float(self.numpad.lineEdit.text()) * 100), selected_user))
            conn.commit()
            self.numpad.lineEdit.clear()
            self.load_table()
            self.stack.setCurrentWidget(self.landing)
        except ValueError as e:
            print(e)

    def write_charge(self):
        try:
            selected_user = self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 0).text()
            selected_bill = self.landing.tableWidget.item(self.landing.tableWidget.currentRow(), 1).text()
            conn.execute('''UPDATE user_bills
                                            SET bill = ?
                                            WHERE user_id = (SELECT id FROM user_login 
                                                             WHERE username = ?);''',
                         (int(float(selected_bill) * 100) + int(float(self.numpad.lineEdit.text()) * 100), selected_user))
            conn.commit()
            self.numpad.lineEdit.clear()
            self.load_table()
            self.stack.setCurrentWidget(self.landing)
        except ValueError as e:
            print(e)

    def back(self):
        self.load_table()
        window.to_admin_options_page()


# ------------------Individual/reusable widget defining classes below--------------------------------------------------

# TODO move these to separate files
class NumpadWidgetUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NumpadWidgetUI, self).__init__(parent)
        loadUi('numpad.ui', self)

        self.pushButton_1.clicked.connect(lambda: self.add_number(1))
        self.pushButton_2.clicked.connect(lambda: self.add_number(2))
        self.pushButton_3.clicked.connect(lambda: self.add_number(3))
        self.pushButton_4.clicked.connect(lambda: self.add_number(4))
        self.pushButton_5.clicked.connect(lambda: self.add_number(5))
        self.pushButton_6.clicked.connect(lambda: self.add_number(6))
        self.pushButton_7.clicked.connect(lambda: self.add_number(7))
        self.pushButton_8.clicked.connect(lambda: self.add_number(8))
        self.pushButton_9.clicked.connect(lambda: self.add_number(9))
        self.pushButton_0.clicked.connect(lambda: self.add_number(0))
        self.pushButton_del.clicked.connect(self.lineEdit.backspace)
        self.pushButton_clr.clicked.connect(self.lineEdit.clear)

    def add_number(self, number):
        self.lineEdit.insert(str(number))

    def set_money_mode(self):
        self.lineEdit.setMaxLength(6)
        self.pushButton_login.setText('Enter')
        validator = QDoubleValidator(0, 100, 2, self)
        self.lineEdit.setValidator(validator)
        self.pushButton_clr.setText('.')
        self.pushButton_clr.clicked.disconnect()
        self.pushButton_clr.clicked.connect(partial(self.add_number, '.'))


class UserListWidgetUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UserListWidgetUI, self).__init__(parent)
        loadUi('userList.ui', self)

        self.add_names()

    def add_names(self):
        self.listWidget.clear()
        selection = conn.execute('SELECT USERNAME FROM user_login')
        for row in selection:
            self.listWidget.addItem(row[0])


class CreateUserFormUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CreateUserFormUI, self).__init__(parent)
        loadUi('create_user_form.ui', self)


class VirtualKeyboardUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VirtualKeyboardUI, self).__init__(parent)
        loadUi('keyboard.ui', self)

        self.pushButton_q.clicked.connect(lambda: self.add_letter('q'))
        self.pushButton_w.clicked.connect(lambda: self.add_letter('w'))
        self.pushButton_e.clicked.connect(lambda: self.add_letter('e'))
        self.pushButton_r.clicked.connect(lambda: self.add_letter('r'))
        self.pushButton_t.clicked.connect(lambda: self.add_letter('t'))
        self.pushButton_y.clicked.connect(lambda: self.add_letter('y'))
        self.pushButton_u.clicked.connect(lambda: self.add_letter('u'))
        self.pushButton_i.clicked.connect(lambda: self.add_letter('i'))
        self.pushButton_o.clicked.connect(lambda: self.add_letter('o'))
        self.pushButton_p.clicked.connect(lambda: self.add_letter('p'))
        self.pushButton_a.clicked.connect(lambda: self.add_letter('a'))
        self.pushButton_s.clicked.connect(lambda: self.add_letter('s'))
        self.pushButton_d.clicked.connect(lambda: self.add_letter('d'))
        self.pushButton_f.clicked.connect(lambda: self.add_letter('f'))
        self.pushButton_g.clicked.connect(lambda: self.add_letter('g'))
        self.pushButton_h.clicked.connect(lambda: self.add_letter('h'))
        self.pushButton_j.clicked.connect(lambda: self.add_letter('j'))
        self.pushButton_k.clicked.connect(lambda: self.add_letter('k'))
        self.pushButton_l.clicked.connect(lambda: self.add_letter('l'))
        self.pushButton_z.clicked.connect(lambda: self.add_letter('z'))
        self.pushButton_x.clicked.connect(lambda: self.add_letter('x'))
        self.pushButton_c.clicked.connect(lambda: self.add_letter('c'))
        self.pushButton_v.clicked.connect(lambda: self.add_letter('v'))
        self.pushButton_b.clicked.connect(lambda: self.add_letter('b'))
        self.pushButton_n.clicked.connect(lambda: self.add_letter('n'))
        self.pushButton_m.clicked.connect(lambda: self.add_letter('m'))

        self.pushButton_del.clicked.connect(self.lineEdit.backspace)

    def add_letter(self, letter):
        self.lineEdit.insert(letter)


class MenuButtonFieldUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MenuButtonFieldUI, self).__init__(parent)
        loadUi('menu_button_field.ui', self)


class NewMenuItemFormUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NewMenuItemFormUI, self).__init__(parent)
        loadUi('create_menu_item.ui', self)


class EditBillsLandingUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EditBillsLandingUI, self).__init__(parent)
        loadUi('edit_bill_table.ui', self)


class PayButtonsUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PayButtonsUI, self).__init__(parent)
        loadUi('pay_buttons.ui', self)


# --------------------Utility classes below-------------------------

# TODO Session class to store user data across pages. Should be a singleton.
class Session:
    def __init__(self, sql_tuple=(None, None, None, None, None,)):
        self.user_id = sql_tuple[0]
        self.username = sql_tuple[1]
        self.privileges = sql_tuple[3]
        self.bill = sql_tuple[4]
        print("Session initialized")

    def start_session(self, sql_tuple):
        self.user_id = sql_tuple[0]
        self.username = sql_tuple[1]
        self.privileges = sql_tuple[3]
        self.bill = sql_tuple[4]
        print("Session started")

    def end_session(self):
        self.user_id = None
        self.username = None
        self.privileges = None
        self.bill = None
        print("Ended session")

# TODO this doesn't need to be here, move it to login page class, only place it's used
    def authenticate(self, sql_tuple, pwentry):
        pwhash = sql_tuple[2]
        if pbkdf2_sha256.verify(pwentry, pwhash):
            return True
        else:
            return False

try:
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    conn.execute('''CREATE TABLE IF NOT EXISTS user_login
                                (id          INTEGER     PRIMARY KEY  AUTOINCREMENT,
                                 username    TEXT        NOT NULL       UNIQUE,
                                 pwhash      VARCHAR     NOT NULL,
                                 privileges  CHAR(1)  NOT NULL);''')
    conn.execute('''CREATE TABLE IF NOT EXISTS menu_items
                                    (id           INTEGER          PRIMARY KEY    AUTOINCREMENT,
                                     item_name    TEXT             NOT NULL       UNIQUE,
                                     price        DECIMAL(5,2)     NOT NULL,
                                     category     TEXT             NOT NULL,
                                     icon_path    VARCHAR);''')
    conn.execute('''CREATE TABLE IF NOT EXISTS user_bills
                                    (user_id     INTEGER       NOT NULL    PRIMARY KEY     UNIQUE,
                                     bill        INTEGER  NOT NULL);''')

    conn.commit()

# TODO Fix this broad except
except Exception as e:
    print(e)
    print("No such database")

user_session = Session()
ROOT_DIR = os.path.curdir
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.showFullScreen()
    app.exec_()
