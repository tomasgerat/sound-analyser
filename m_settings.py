from qt import QSettings

class M_Settings(QSettings):
    def __init__(self, path):
        super().__init__()
        print("[Settings]", path)
        self.setPath(self.IniFormat, self.UserScope, path)

    def get_accepted_classes(self):
        self.beginGroup("GLOBAL")
        classes = self.value("classes", "").split(";")
        self.endGroup()
        print("Accepted classes:", classes)
        return classes

    def set_accepted_classes(self, classes):
        print("Save accepted classes", classes)
        output=""
        for c in classes:
            if len(output) == 0:
                output = c
            else:
                output = output + ";" + c
        self.beginGroup("GLOBAL")
        self.setValue("classes", output)
        self.endGroup()