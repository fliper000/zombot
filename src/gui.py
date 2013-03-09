import sys
from PyQt4 import QtGui
app = QtGui.QApplication(sys.argv)


def raw_input(prompt):
    prompt = prompt.decode('utf-8')
    title = prompt.split('\n')[0].split(':')[0]
    input_dialog = QtGui.QInputDialog()
    items = filter(None, prompt.split('\n')[1:])
    input_dialog.setComboBoxItems(items)
    input_dialog.setLabelText(title)
    input_dialog.setOptions(QtGui.QInputDialog.UseListViewForComboBoxItems)
    done = input_dialog.exec_()
    user_choice = input_dialog.textValue()

    if not done:
        sys.exit(-1)
    return items.index(unicode(user_choice)) + 1
