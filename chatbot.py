from bs4 import BeautifulSoup
import requests
import uuid
import time
import json

# Надо сделать 2 класса, 1- с моделью (хранение и представление данных) рецепта и класс для парсера
# (который собирает данные)

class Recipe:
    def __init__(self,main_picture ,recipe_name ,cooking_time ,portion ,ingredients ,description ,cooking_steps ,cooking_steps_pictures ,url):
        self.main_picture = main_picture
        self.recipe_name = recipe_name
        self.cooking_time = cooking_time
        self.portion = portion
        self.ingredients = ingredients
        self.description = description
        self.cooking_steps = cooking_steps
        self.cooking_steps_pictures = cooking_steps_pictures
        self.url = url

    def __repr__(self):
        return f'Рецепт: {self.recipe_name}'

    def to_dict(self):
        return {
        'main_picture': self.main_picture,
        'recipe_name': self.recipe_name,
        'cooking_time': self.cooking_time,
        'portion': self.portion,
        'ingredients': self.ingredients,
        'description': self.description,
        'cooking_steps': self.cooking_steps,
        'cooking_steps_pictures': self.cooking_steps_pictures,
        'url': self.url
        }


class Parser:
    def __init__(self):
        self.main_url = 'https://vege.one'
        with open('links.json', 'r') as f:
            self.all_links = json.load(f)

    def pars_recipe(self, url):
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        recipe_name = ''
        recipe_steps_list = []
        cooking_time = ''
        portion = ''
        ingredients_data = {}
        main_picture = ''
        cooking_steps_pictures = []

        main_recipe_stages_class = 'recipe_stages end_page_headers text-container with-bg'
        recipe_stage_class = 'recipe_stage instruction d-flex flex-wrap flex-lg-nowrap'
        description_class = 'desc_text description text-container'
        cooking_time_class = 'value duration'
        portion_class = 'portion yield'
        ingredients_class = 'toggle-content'
        main_picture_class = 'w-100 mb-0 recipe-main-image photo result-photo'



        ingredients = soup.find('ul', class_= ingredients_class)
        for child in ingredients.contents:
            if len(child.contents)>1:
                food_name = child.contents[0].get_text().strip()
                measure = child.contents[1].get_text().strip()
            else:
                food_name = child.contents[0].get_text().strip()
                measure = ''
            ingredients_data[food_name] = measure


        recipe_description = soup.find('div', class_= description_class)
        # print(recipe_description.get_text().strip())



        recipe_block = soup.find('div', class_= main_recipe_stages_class)
        recipe_name = soup.find ('h1', class_ = 'recipe_title w-100 fn')
        recipe_name = recipe_name.get_text().strip()
        # print(recipe_name)

        for stage_element in recipe_block.find_all('div', class_=recipe_stage_class):
            s = stage_element.get_text().strip()
            while '  ' in s:
                s = s.replace('  ', ' ')
            s = s.replace('\n', '')
            for i, letter in enumerate(s[:6]):
                if not letter.isnumeric():
                    s = s[:i]+"."+s[i:]
                    break
            recipe_steps_list.append((s))
        # print(recipe_steps_list)

        cooking_steps_picture = soup.find_all ('div', class_='stage_img d-inline-block')
        # print (cooking_steps_picture[0].contents[1].attrs['data-src'])
        b = []
        for tag in cooking_steps_picture:
            b.append(tag.contents[1].attrs['data-src'])

        cooking_steps_pictures = self.download_images(b)
        # print(cooking_steps_pictures)

        cooking_time = soup.find('span', class_= cooking_time_class)
        # print(cooking_time.get_text().strip())

        portion = soup.find('span', class_= portion_class)
        if not portion:
            portion = soup.find('span', class_='portion')

        # print(portion.get_text().strip())

        main_picture = soup.find('img', class_ = main_picture_class)
        if main_picture:
            # print (main_picture.attrs['src'])
            a = [main_picture.attrs['src']]
            main_picture_name = self.download_images(a)[0]
        else:
            main_picture_name = None

        result_recipe = Recipe(
            main_picture_name ,
            recipe_name ,
            cooking_time.get_text().strip() ,
            portion.get_text().strip(),
            ingredients_data ,
            recipe_description.get_text().strip() ,
            recipe_steps_list ,
            cooking_steps_pictures ,
            url)
        return result_recipe

    def pars_all_recipes(self):
        all_parsed_recipes = []
        k = 0
        for i in self.all_links[:11]:
            print (i)
            all_parsed_recipes.append(self.pars_recipe(i).to_dict())
            print(f'Спрасили {k}-ый рецепт')
            k+=1
        with open('recipes.json', 'w', encoding='utf8') as f:
            json.dump(all_parsed_recipes, f, ensure_ascii=False)


    def download_images(self, urls):
        names = []
        for url in urls:
            if not url:
                continue

            response = requests.get(self.main_url + url)

            file_extension = url[url.find('.'):]
            name = str(uuid.uuid4()) + file_extension

            file = open("images/"+name, "wb")
            file.write(response.content)
            file.close()

            names.append(name)
        return names

    def pars_all_links (self):
        parsing_page = 'https://vege.one/recipes/?PAGEN_1='
        for i in range(1,153):
            response = requests.get(parsing_page+str(i))
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            link_class = "dds_link_title"
            link_collection = soup.find_all('a', class_= link_class)
            for link in link_collection:
                all_text_link = self.main_url+link.attrs['href']
                self.all_links.append(all_text_link)
            print(f'The {i}-th page parsed')
        # with open('links.json', 'w') as f:
        #    json.dump(self.all_links, f)
        print (self.all_links)
        print(len(self.all_links))


p = Parser ()


start = time.time()
# result = p.pars_recipe('https://vege.one/recipes/veganskie-retsepty/vtorye-blyuda/nutovyi-omlet-s-tofu-i-ovoshchami-k-zavtraku/')
# print(result)
# print(result.__dict__)
end = time.time()
# print(end - start)
# result = p.pars_all_links()

result = p.pars_all_recipes()


# TODO: Проверить, почему не скачалась картинка отсюда https://vege.one/recipes/veganskie-retsepty/veganskie-supy/gribnoy-sup-s-pshenom/
