from tools.helpers.interface.wrappers import (_messagebox, _MessageBox,
                                              _simpledialog, _SimpleDialog,
                                              _filedialog, _FileDialog)

# Import custom dialogs
from tools.helpers.interface.custom_messagebox import ask_custom_question
from tools.helpers.interface.custom_dialog import (ask_multiple_questions, ask_option, ask_checkbox,
                                                   ask_radio_button)
from tools.helpers.interface.text_frame import showtext
from tools.helpers.interface.date_picker import get_user_date


class _AdvancedMessageBox(_MessageBox):  # inheritance is just for IDE to show attributes
    """Add custom dialogs to messagebox"""
    _base_module = _messagebox
    # For signature in IDE
    showtext = showtext
    askcustomquestion = ask_custom_question

    _custom_func = {'showtext': showtext,
                    'askcustomquestion': askcustomquestion,
                    }


class _AdvancedSimpleDialog(_SimpleDialog):  # inheritance is just for IDE to show attributes
    """Add custom dialogs to simpledialog"""
    _base_module = _simpledialog
    # For signature in IDE
    askoption = ask_option
    askcheckbox = ask_checkbox
    askradiobutton = ask_radio_button
    ask_multiple_questions = ask_multiple_questions
    askdate = get_user_date

    _custom_func = {'askoption': askoption,
                    'askcheckbox': askcheckbox,
                    'askradiobutton': askradiobutton,

                    'askdate': askdate,

                    'ask_multiple_questions': ask_multiple_questions,
                    }


class _AdvancedFileDialog(_FileDialog):  # inheritance is just for IDE to show attributes
    """Add custom dialogs to simpledialog"""
    _base_module = _filedialog


messagebox = _AdvancedMessageBox()
simpledialog = _AdvancedSimpleDialog()
filedialog = _AdvancedFileDialog()

if __name__ == '__main__':
    print(messagebox.askokcancel(message='OK?'))
    print(messagebox.showtext(text="Hello!"))
    print(messagebox.askcustomquestion(choices=[1, 2]))

    print(simpledialog.askinteger(title='title', prompt='Integer?'))
    print(simpledialog.askdate(title='title'))
    print(simpledialog.askoption(choices=[4, 5]))
    print(simpledialog.askcheckbox(choices=[4, 5]))
    print(simpledialog.askradiobutton(choices=[4, 5]))
    print(simpledialog.ask_multiple_questions(multi_choices=[[1, 2]]))
