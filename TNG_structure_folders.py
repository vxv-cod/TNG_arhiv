import os
import shutil
import sys
# from transliterate import translit
from PyQt5 import QtCore, QtWidgets

import vxv_translitt_text
from Options import *
from okno_ui import Ui_Form

# from rich import print

app = QtWidgets.QApplication(sys.argv)
Form = QtWidgets.QWidget()
ui = Ui_Form()
ui.setupUi(Form)
Form.show()


_translate = QtCore.QCoreApplication.translate
Title = 'Доработка структуры папок для Заказчика'
Form.setWindowTitle(_translate("Form", Title))


def GO(directory):
    progressBar = ui.progressBar_1

    sig.signal_Probar.emit(progressBar, 5)
    result_folder = directory.rsplit("\\", 1)[0] + "\\Result"
    try:
        os.mkdir(result_folder)
    except:
        try:
            shutil.rmtree(result_folder)
        except FileNotFoundError:
            sig.signal_label.emit(ui.label, '')
            return sig.signal_err.emit(Form, "Адресс не найден ! ! !")
            
        os.mkdir(result_folder)
    sig.signal_Probar.emit(progressBar, 10)

    def pointdel(text):
        '''Заменяем точки до расширения файла'''
        xxx = text.rsplit(".", 1)
        aaa = vxv_translitt_text.GO(xxx[0])
        aaa = aaa.replace("-RS", "-rC")
        aaa = aaa.replace("-RC", "-rC")
        name = aaa + "." + xxx[1].lower()
        return name

    '''
    Собираем:
        полный путь исходного файла
        локальное имя файла, с заменой точек на _
        полные пути новых папок
    '''
    fails_patch = []
    fails_name = []
    newfolders = []

    for Patch, dirs, files in os.walk(directory):
        if files != []:
            for name in files:
                PatchList = Patch.rsplit("\\", 1)
                
                newfolder = vxv_translitt_text.GO(PatchList[1])
                newfolder = newfolder.upper().replace("_REV_", "-r")
                
                fails_patch.append(os.path.join(Patch, name))
                # name = vxv_translitt_text.GO(name)
                fails_name.append(pointdel(name))
                # fails_name.append(vxv_translitt_text.GO(name))
                
                newPatch = f"{result_folder}\\{newfolder}"
                newfolders.append(newPatch)
                
    sig.signal_Probar.emit(progressBar, 20)
    
    # print(f'fails_patch = {fails_patch}')
    # print(f'fails_name = {fails_name}')
    # print(f'newfolders = {newfolders}')

    try:
        for d in set(newfolders):
            os.makedirs(f"{d}\FR")
    except:
        print(f'Не удалось создать папку "FR" в: {d}')

    for index, fail in enumerate(fails_name):
        if ".pdf" in fail:
            shutil.copy2(fails_patch[index], newfolders[index] + "\\" + fails_name[index])
        
        if ".zip" in fail:
            patchzip = newfolders[index] + "\\FR"
            shutil.unpack_archive(fails_patch[index], patchzip)


            # Заменяем "-RC" из названия файла в папке с распакованным архивом
            for Patch, dirs, files in os.walk(patchzip):
                for na in files:
                    if "-RC" in na.upper():
                        NewNameArxivFaile = na.upper().replace("-RC", "-rC")
                        NewNameArxivFaile = pointdel(NewNameArxivFaile)
                        try:
                            # Переименовываем файл
                            os.rename(Patch + "\\" + na, Patch + "\\" + NewNameArxivFaile)
                        except:
                            # Удаляем файл с именем файла идентичным с именем сохранения нового файла
                            os.remove(os.path.join(Patch, NewNameArxivFaile))
                            # Переименовываем файл
                            os.rename(Patch + "\\" + na, Patch + "\\" + NewNameArxivFaile)
        

        if ".pdf" not in fail and ".zip"not in fail:
            shutil.copy2(fails_patch[index], newfolders[index] + "\\FR\\" + fails_name[index])

    '''Проходим по результирующей папке в поисках архива и распаковываем его в папки FR'''
    for Patch, dirs, files in os.walk(result_folder):
        for name in files:
            # print(f'name = {name}')
            name = name.replace(".ZIP", ".zip")
            if ".zip" in name:
                fullname = os.path.join(Patch, name)
                namearhivALL = os.path.splitext(name)
                namearhiv = namearhivALL[0]
                tmp_dir = Patch + "\\" + namearhiv
                '''Разархивируем в туже папку с названием как архив'''
                shutil.unpack_archive(fullname, tmp_dir)
                '''Удаляем архив'''
                os.remove(fullname)
                '''Проходим по временным папкам с названием как был архив'''
                for Patch_, dirs_, files_ in os.walk(tmp_dir):
                    for name_ in files_:
                        namefile_suffix = os.path.splitext(name_)[1]
                        oldname_ = os.path.join(Patch_, name_)
                        newname_ = os.path.join(Patch_, name_)
                        if ".png" not in namefile_suffix.lower():
                            newname_ = os.path.join(Patch_, namearhiv + namefile_suffix)
                            '''Переименовываем в этих папках файлы, которые не PNG'''
                            os.rename(oldname_, newname_)
                        try:
                            '''Перемещаем файлы из папки на верх в FR'''
                            shutil.move(newname_, Patch)
                        except:
                            '''Файлы с совпадающим именем не трогаем'''
                            pass
                    '''Удаляем папки после изътия из них нужных файлов'''
                    print(f'Patch_ = {Patch_}')
                    shutil.rmtree(Patch_)

    '''Проходим по всем файлам и переводим на латиницу, заменяя имя файла'''
    for Patch, dirs, files in os.walk(result_folder):
        for name in files:
            if ".png" not in name.lower():
                fullname = os.path.join(Patch, name)
                newname =  os.path.join(Patch, pointdel(name))
                os.rename(fullname, newname)


    sig.signal_Probar.emit(progressBar, 50)

    if ui.checkBox.isChecked() == True:
        '''Архивируем вложенные папки в результирующей папке'''
        listdir_name = os.listdir(result_folder)
        listdir_patch =  [os.path.join(result_folder, name) for name in listdir_name]
        for i, folder in enumerate(listdir_name):
            archive_name = os.path.join(result_folder, folder)
            shutil.make_archive(archive_name, 'zip', listdir_patch[i])

        '''Удаляем папки, которые уже заархивированные'''
        for i, folder in enumerate(listdir_patch):
            shutil.rmtree(folder)
    
    sig.signal_Probar.emit(progressBar, 100)
    sig.signal_label.emit(ui.label, 'Готово. Создана папка " Result " рядом с иходной')


sig = Signals()



@thread
@startFun(Form, sig, [ui.pushButton], ui.progressBar_1, ui.label)
def start():

    directory = ui.plainTextEdit.toPlainText()
    if directory == '':
        sig.signal_label.emit(ui.label, '')
        return sig.signal_err.emit(Form, "Не указана исходная папка ! ! !")
    GO(directory)
    

ui.plainTextEdit.clear()
ui.plainTextEdit.textChanged.connect(lambda : ChangedPT(ui.plainTextEdit))

ui.pushButton.clicked.connect(start)



if __name__ == "__main__":
    sys.exit(app.exec_())