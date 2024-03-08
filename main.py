from telebot.async_telebot import AsyncTeleBot as telebot
import telebot.types as tps
import asyncio
import config
import text

class Bot:
    def __init__(self):
        self.TOKEN = config.token
        self.bot = telebot(self.TOKEN)

        self.users = []

        self.check_if_userlist_file_exist()
        self._update()

    def _update(self):
        @self.bot.message_handler(commands=['start', 'feedback'])
        async def handle_start(message):
            if message.text == "/start":
                if self.check_if_user_already_exist_in_userlist(message.chat.id):
                    await self.bot.send_message(message.chat.id, text.welcome_message, parse_mode="HTML")
                elif not self.check_if_user_already_exist_in_userlist(message.chat.id):
                    try: 
                        self.markup = tps.InlineKeyboardMarkup()
                        self.anonymous = tps.InlineKeyboardButton(text.yes_want, callback_data='yes')
                        self.noanonymous = tps.InlineKeyboardButton(text.no_want, callback_data='no')
                        self.markup.row(self.anonymous, self.noanonymous)
                        
                        await self.bot.send_message(message.chat.id, text.share_image, reply_markup=self.markup, parse_mode="HTML")
                    except:
                        print("ERROR")

            if message.text.split()[0] == "/feedback":
                try:
                    print(message.text.split()[1])
                    await self.bot.forward_message(config.admin, message.chat.id, message.id)
                    await self.bot.send_message(message.chat.id, text=text.sent_well)
                except:
                    await self.bot.send_message(message.chat.id, text=text.wrong_feedback)
        
        @self.bot.message_handler(content_types=['photo'])
        async def handle_photo(message):
            if self.check_if_user_already_exist_in_userlist(message.chat.id):
                try:
                    await self.bot.forward_message(config.admin, message.chat.id, message.id)

                    if self.check_if_user_anonymous(message.chat.id):
                        await self.bot.send_message(config.admin, text=f"{text.anonymous_user}")
                    elif not self.check_if_user_anonymous(message.chat.id):
                        await self.bot.send_message(config.admin, text=f"{text.no_anonymous_user}\nUsuario: @{message.from_user.username}")
    
                    await self.bot.send_message(message.chat.id, text=text.sent_well)
                except:
                    await self.bot.send_message(message.chat.id, text=text.sent_wrong)
            elif not self.check_if_user_already_exist_in_userlist(message.chat.id):
                await self.bot.send_message(message.chat.id, text=text.please_register)

        @self.bot.callback_query_handler(func=lambda call: True)
        async def handle_buttons(call):
            if not self.check_if_user_already_exist_in_userlist(call.message.chat.id):
                if call.data == "yes":
                    print("user yes")
                    self.add_user_to_list(call.message.chat.id, True)
                    await self.bot.delete_message(call.message.chat.id, call.message.id)
                    await self.bot.send_message(call.message.chat.id, text=text.correctly_yes)
                elif call.data == "no":
                    print("user no")
                    self.add_user_to_list(call.message.chat.id, False)
                    await self.bot.delete_message(call.message.chat.id, call.message.id)
                    await self.bot.send_message(call.message.chat.id, text=text.correctly_no)
            try:
                if self.check_if_user_already_exist_in_userlist(call.message.chat.id):
                    print("user already registered trying to use buttons")
                    await self.bot.delete_message(call.message.chat.id, call.message.id)
            except:
                pass

        asyncio.run(self.bot.polling(none_stop=True))

    def load_users_and_append(self):
        print("Load de users from the file and add them")
        print(self.users)
        self.clean_list()
        with open("users.txt", "r") as self.users_list:
            for self.user in self.users_list.read().split("\n"):
                if not self.user == "" and not self.user in self.users:
                    self.users.append(self.user)
        print(self.users)

    def check_if_userlist_file_exist(self):
        print("Check if userlist file exists")
        try:
            self.load_users_and_append()
        except:
            open("users.txt", "w")

    def check_if_user_already_exist_in_userlist(self, user_id):
        print("Check if the user is already in the userlist")
        print(self.users)
        for self.u in self.users:
            print(self.u)
            if user_id == int(self.u.split(":")[0]):
                print(f"User '{user_id}' is in the list")
                return True
    
    def clean_list(self):
        print("Clean the list of users")
        self.users = []

    def add_user_to_list(self, user, anonymous):
        print("Add a user to the users list")
        with open("users.txt", "a") as self.users_list:
            if not self.check_if_user_already_exist_in_userlist(user): 
                if anonymous:
                    self.users_list.write(f"{user}:{1}\n")
                elif not anonymous:
                    self.users_list.write(f"{user}:{0}\n")
        self.load_users_and_append()

    def check_if_user_anonymous(self, user):
        print("Check if user is anonymous")
        for self.use in self.users:
            if user == int(self.use.split(":")[0]):
                if int(self.use.split(":")[1]) == 1:
                    print("Anonymous")
                    return True
                if int(self.use.split(":")[1]) == 0:
                    print("No anonymous")
                    return False

def main():
    Bot()

if __name__ == "__main__":
    main()