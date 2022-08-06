import telebot
from telebot import types
import random
import json

from telebot.types import InputMediaPhoto

class RecipeEngine:
    def __init__(self):
        with open('recipes.json', 'r', encoding='utf8') as f:
            self.recipes = json.load(f)

    def get_random_recipe(self):
        return random.choice(self.recipes)

    def get_recipe_text_view(self, recipe):
        text = ''
        text += recipe['recipe_name'] + '\n\n'
        text += "Готовить примерно " + recipe['cooking_time'] + '\n'
        text += 'Получится ' + recipe['portion'] + '\n\n'
        text += "Ингредиенты:" + '\n'
        for key, value in recipe['ingredients'].items():
            text += "• " + key + " " + value + '\n'
        text += '\n' + recipe['description'] + '\n'
        text += '\n\nКак готовить \n\n'
        for step in recipe['cooking_steps']:
            text += step + '\n\n'
        text += "Подробности тут: " + recipe['url']
        return text

    def get_reciepe_by_ingredient(self, ingregient):
        recipes_to_send = []
        for recipe in self.recipes:
#            if ingregient.lower() in recipe["ingredients"].keys():
# Может быть и так
            if ingregient.lower() in map(lambda x: x.lower(), recipe["ingredients"].keys()):
                recipes_to_send.append(recipe)
            if len(recipes_to_send)>3:
                return recipes_to_send
        return recipes_to_send



vegerecipesbot = telebot.TeleBot("5324211853:AAHgF2PBs4D4l-O3d_yxuy9pruTI1ckp6hE", parse_mode=None)
previous_message = ''
any_recipe = RecipeEngine()

def send_recipe(recipe, message):
    image_of_recipe = recipe['main_picture']
    media_group = []

    if image_of_recipe:
        img = open("images/" + image_of_recipe, 'rb')
        vegerecipesbot.send_photo(message.chat.id, img)
        img.close()
    vegerecipesbot.send_message(message.chat.id, any_recipe.get_recipe_text_view(recipe), reply_markup=make_markup())
    if len(recipe['cooking_steps_pictures']) > 1:
        # TODO: надо переделать условие, потому что с одной картинкой сей код не сработает
        for image in recipe['cooking_steps_pictures']:
            media_group.append(
                InputMediaPhoto(
                    open("images/" + image, 'rb'),
                    caption=f'Шаг приготовления {recipe["cooking_steps_pictures"].index(image) + 1}'
                ))
        vegerecipesbot.send_media_group(chat_id=message.chat.id, media=media_group)

    else:
        vegerecipesbot.send_message(message.chat.id, "Поиск", reply_markup=make_markup())


@vegerecipesbot.message_handler(commands=['start', 'help'])
def first_message(message):
    vegerecipesbot.send_message(message.chat.id, "Нажмите на кнопку", reply_markup=make_markup())

def make_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Случайный рецепт')
    itembtn2 = types.KeyboardButton('Найти рецепт по одному ингредиенту')
    markup.add(itembtn1, itembtn2)
    return markup


@vegerecipesbot.message_handler(func=lambda message: message.text == 'Случайный рецепт')
def random_reciepe(message):
    any_recipe = RecipeEngine()
    send_recipe(any_recipe.get_random_recipe(), message)

@vegerecipesbot.message_handler(func=lambda message: message.text == 'Найти рецепт по одному ингредиенту')
def reciepe_by_ingr(message):
    vegerecipesbot.send_message(message.chat.id, "Напишите название ингредиента", reply_markup=make_markup())
    global previous_message
    previous_message = message.text

@vegerecipesbot.message_handler(func=lambda message: True)
def send_resipe_by_ingr(message):
    global previous_message
    vegerecipesbot.send_message(message.chat.id, "Нажмите на кнопку", reply_markup=make_markup())
    if previous_message == 'Найти рецепт по одному ингредиенту':
        for recipe in any_recipe.get_reciepe_by_ingredient(message.text):
            send_recipe(recipe, message)
    previous_message = None







vegerecipesbot.infinity_polling()
