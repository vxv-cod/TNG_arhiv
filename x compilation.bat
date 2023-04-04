pyinstaller -w -F -i "logo.ico" TNG_structure_folders.py

xcopy %CD%\*.ico %CD%\dist /H /Y /C /R

xcopy C:\vxvproj\tnnc-TNG_arhiv\dist C:\vxvproj\tnnc-TNG_arhiv\ConsoleApp\ /H /Y /C /R
