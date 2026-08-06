from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
)

from config import BOT_TOKEN

from bot.handlers import (
    start,
    button_handler
)



def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )


    print(
        "TourHunter v0.2 работает..."
    )


    app.run_polling()



if __name__ == "__main__":
    main()