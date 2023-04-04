from PyQt5 import QtCore, QtWidgets
import os
import threading
import pyodbc
import time
import traceback



def Sql(text):
    """Модуль отправки данный на MS SQL 2017 server силами Python"""
    '''Формируем текущую дату'''
    sec = time.localtime(time.time())
    now = f'{sec.tm_mday}-{sec.tm_mon}-{sec.tm_year} {sec.tm_hour}:{sec.tm_min}:{sec.tm_sec}'

    '''Формируем имя пользователя'''
    username = "ROSNEFT\\" + os.getlogin()

    '''Далее создаём строку подключения к нашей базе данных:'''
    connectionString = ("Driver={SQL Server};"
                        "Server=10.28.150.35;"
                        "Database=TNNC_OAPR_STAT;"
                        "UID=TNNC_OAPR_STAT;"
                        "PWD=RhbgjdsqGfhjkmLkz<L!&$(")

    '''После заполнения строки подключения данными, выполним соединение к нашей базе данных:'''
    connection = pyodbc.connect(connectionString, autocommit=True)

    '''Создадим курсор, с помощью которого, посредством передачи 
    запросов будем оперировать данными в нашей таблице:'''
    dbCursor = connection.cursor()

    '''Добавим данные в нашу таблицу с помощью кода на python:'''
    requestString = f'''INSERT INTO [dbo].StatTable(UserName, ApplicationName, UsingTime) 
                        VALUES  ('{username}', '{text}', '{now}')'''
    dbCursor.execute(requestString)

    '''Сохранение данный в базе'''
    connection.commit()
    print("Отпавка записи на сервер статистики")



class Signals(QtCore.QObject):
    '''
    sig.signal_Probar.emit(ui.progressBar_1, 100)
    sig.signal_label.emit(ui.label, "Выполнено")
    sig.signal_err.emit(f"Ошибка работы, повторите попытку \n\n{traceback.format_exc()}")
    sig.signal_color.emit(ui.progressBar_1, 0)
    sig.signal_color.emit(ui.progressBar_1, 1)
    sig.signal_bool.emit(ui.pushButton, True)
    sig.signal_bool.emit(ui.pushButton, False)
    '''
    signal_Probar = QtCore.pyqtSignal(QtWidgets.QWidget, int)
    signal_label = QtCore.pyqtSignal(QtWidgets.QWidget, str)
    signal_err = QtCore.pyqtSignal(QtWidgets.QWidget, str)
    signal_bool = QtCore.pyqtSignal(QtWidgets.QWidget, bool)
    signal_color = QtCore.pyqtSignal(QtWidgets.QWidget, int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.signal_Probar.connect(self.on_change_Probar,QtCore.Qt.QueuedConnection)
        self.signal_label.connect(self.on_change_label,QtCore.Qt.QueuedConnection)
        self.signal_err.connect(self.on_change_err,QtCore.Qt.QueuedConnection)
        self.signal_bool.connect(self.on_change_bool,QtCore.Qt.QueuedConnection)
        self.signal_color.connect(self.on_change_color,QtCore.Qt.QueuedConnection)

    '''Отправляем сигналы в элементы окна'''
    def on_change_Probar(self, s1, s2):
        '''Значение процента в прогресбаре'''
        s1.setValue(s2)
    def on_change_label(self, s1, s2):
        '''Отправляем текст в label'''
        s1.setText(s2)
    def on_change_err(self, s1, s2):
        '''Сообщение об ошибке'''
        QtWidgets.QMessageBox.information(s1, 'Сбой программы...', s2)
    def on_change_color(self, s1, s2):
        '''Устанавливаем цвет прогресбара'''
        if s2 == 1:
            color = "170, 170, 170"
        else:
            color = "100, 150, 150"
        s1.setStyleSheet("QProgressBar::chunk {background-color: rgb("f"{color}); margin: 2px;""}")
    def on_change_bool(self, s1, s2):
        s1.setDisabled(s2)

# sig = Signals()



'''Обертка функции в потопк (декоратор)'''
def thread(my_func1):
    def wrapper():
        threading.Thread(target=my_func1, daemon=True).start()
    return wrapper


def startFun(Form, sig, pushButtonList, progressBar, label):
    '''Обертка в декоратор с параметрами'''
    def real_decor(my_func):
        def wrapper():
            """Обертка функции (декоратор)"""
            Sql("TNG_structure_folders")
            
            try:
                for i in pushButtonList:
                    sig.signal_bool.emit(i, True)
                sig.signal_label.emit(label, "Обработка данных . . .")
                sig.signal_Probar.emit(progressBar, 0)
                sig.signal_color.emit(progressBar, 0)
                my_func()
            except:
                errortext = traceback.format_exc()
                print(errortext)
                text = f"Ошибка работы, повторите попытку \n\n{errortext}"
                sig.signal_err.emit(Form, text)
                # sig.signal_label.emit(label, '')
            for i in pushButtonList:
                sig.signal_bool.emit(i, False)
            sig.signal_Probar.emit(progressBar, 0)
            sig.signal_color.emit(progressBar, 100)

        return wrapper
    return real_decor





def ChangedPT(plainTextEdit):
    '''Отслеживаем сигнал в plainTextEdit на изменение данных и удаляем не нужный текст'''
    '''Удаления ненужного текста в plainTextEdit_3'''
    directory = plainTextEdit.toPlainText()
    if "file:///" in directory:
        xxx = directory.rfind("file:///")
        directory = directory[xxx + 8:]
        try:
            directory = directory.replace("/", "\\")
        except:
            pass
        plainTextEdit.setPlainText(rf"{directory}")
# ui.plainTextEdit_3.textChanged.connect(lambda : ChangedPT(ui.plainTextEdit_3))


# if __name__ == "__main__":
#     from PyQt5 import QtCore, QtWidgets
#     import os