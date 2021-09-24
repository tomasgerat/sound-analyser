from qt import QCheckBox

class M_CheckBox(QCheckBox):
    def __init__(self, id, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.id_=id

    def id(self):
        return self.id_
