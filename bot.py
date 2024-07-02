import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import qrcode
from io import BytesIO

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

MENU, NAME, PHONE, ORDER_CONFIRMATION = range(4)

menu = {
    "Pizza": 10.0,
    "Burger": 8.0,
    "Sushi": 12.0,
}

def start(update: Update, context: CallbackContext) -> int:
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(item, callback_data=item)] for item in menu.keys()
    ])
    update.message.reply_text("Welcome to our restaurant! Please choose an item from the menu:", reply_markup=reply_markup)
    return MENU

def menu_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    item = query.data
    context.user_data['item'] = item
    context.user_data['price'] = menu[item]
    query.edit_message_text(f"You chose {item}. Please provide your name:")
    return NAME

def name_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text("Please provide your phone number:")
    return PHONE

def phone_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    item = context.user_data['item']
    price = context.user_data['price']
    name = context.user_data['name']
    phone = context.user_data['phone']
    update.message.reply_text(f"Order confirmation:\nItem: {item}\nPrice: ${price}\nName: {name}\nPhone: {phone}\n\nPlease confirm your order by typing 'yes'.")
    return ORDER_CONFIRMATION

def order_confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'yes':
        name = context.user_data['name']
        phone = context.user_data['phone']
        item = context.user_data['item']
        price = context.user_data['price']
        
        # Generate QR code
        qr_data = f"Name: {name}, Phone: {phone}, Item: {item}, Price: {price}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        
        update.message.reply_photo(photo=bio)
        update.message.reply_text("Thank you for your order! A QR code for your payment is generated. Your order will be sent to the kitchen.")
        
        # Simulate sending order to the kitchen (for example, using another Telegram bot or an email)
        kitchen_chat_id = "https://t.me/hhhhhhhhhhhhhtij"
        context.bot.send_message(
            chat_id=kitchen_chat_id,
            text=f"New order:\nName: {name}\nPhone: {phone}\nItem: {item}\nPrice: {price}"
        )
        
        # Send confirmation to user
        update.message.reply_text("Your order has been confirmed. You will receive a discount on your next purchase.")
        context.user_data['discount'] = 10  # Example of discount
        
        return ConversationHandler.END
    else:
        update.message.reply_text("Order cancelled.")
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Order cancelled. See you next time!")
    return ConversationHandler.END

def main():
    updater = Updater("6701923539:AAHUnaECT_EvqUY_jGVqXMFaXfT18-5nlNk")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [CallbackQueryHandler(menu_handler)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name_handler)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone_handler)],
            ORDER_CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, order_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()