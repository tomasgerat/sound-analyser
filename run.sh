echo [GENERATE UI]
#pyside-uic mainWindow.ui > ui_mainWindow.py
pyuic5 mainWindow.ui > ui_mainWindow.py
echo "[START]"
python main.py
