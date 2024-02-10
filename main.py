import contextlib

from logs.mylogging import time_log_decorator

from handlers.command_handlers import add_command_handlers
from handlers.callback_handlers import add_callback_handlers

from handlers.teacher.audio.add import add_audio_conv_handler
from handlers.teacher.audio.edit import edit_audio_conv_handler

from handlers.teacher.victoryna.create import create_victoryna_conv_handler
from handlers.teacher.victoryna.edit import edit_victoryna_conv_handler

from handlers.student.victoryna import student_victoryna_conv_handler

from handlers.error import error

from settings.app import application


@time_log_decorator
def telegram_bot(application):

    add_command_handlers(application)
    add_callback_handlers(application)

    application.add_handler(add_audio_conv_handler)
    application.add_handler(edit_audio_conv_handler)

    application.add_handler(create_victoryna_conv_handler)
    application.add_handler(edit_victoryna_conv_handler)

    application.add_handler(student_victoryna_conv_handler)

    application.add_error_handler(error)

    with contextlib.suppress(KeyboardInterrupt): # Ignore exception when Ctrl-C is pressed
        application.run_polling(0.5)


if __name__ == "__main__":
    telegram_bot(application)
