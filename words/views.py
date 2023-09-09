from django.shortcuts import render
from django.views import View
import os 
import json 
import re
import requests 
from .models import Word
from . word_utils import is_valid_word, is_fancy_word, comp_response_up
# Create your views here.

class HomeView(View):
    template_name = 'home.html'

    @staticmethod
    def get_meaning(word):

        req = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'  
        data = requests.get(req).json()
        return data[0]['meanings'][0]['definitions'][0]['definition'] if len(data) == 1 else "Definition not available."

    def initialize_session(self):
        self.request.session.setdefault('score', 0)
        self.request.session.setdefault('visited_words', [])
        self.request.session.setdefault('all_comp_words', [])


    def process_input(self, current_word):
        return re.sub(r"\s+", "", current_word)


    def get(self, request, *args, **kwargs):
        self.initialize_session()
        context = {'score': 0, 'ending_letter': "NA", 'computer_word': "NA", 'message': "Enter your first word!", 'all_comp_words': []}
        return render(request, self.template_name, context)

    def post(self, request):
        self.initialize_session()
        score = request.session.get('score', 0)
        print(score)
        current_word = request.POST.get('current_word', '').strip()
        all_comp_words = request.session.get('all_comp_words', [])
        visited_words = request.session.get('visited_words', [])
        message, computer_word, ending_letter_comp, comp_word_meaning, right_word = self.handle_word_logic(current_word, score, all_comp_words, visited_words)
        

        request.session['score'] = score 
        request.session['all_comp_words'] = all_comp_words
        request.session['visited_words'] = list(visited_words)

        context = {'score': score, 'comp_word_meaning': comp_word_meaning, 'ending_letter': ending_letter_comp,
                   'computer_word': computer_word, 'message': message, 'all_comp_words': all_comp_words}

        
        return render(request, self.template_name, context)


    def handle_word_logic(self, current_word, score, all_comp_words, visited_words):
        if len(current_word) == 0:
            return "Input is blank.", "NA", "NA", "NA", False 

        right_word = True
        ending_letter_user = current_word[-1]

        if is_valid_word(current_word):
            ending_letter_comp = all_comp_words[-1][-1] if all_comp_words else None
            if ending_letter_comp and current_word[0] != ending_letter_comp:
                return f"Word should begin with the letter: {ending_letter_comp}", "NA", ending_letter_comp, "NA", False

            if is_fancy_word(current_word):
                if current_word in visited_words:
                    return f"{current_word} has already been used.", "NA", ending_letter_comp, "NA", False
                score += 1
                print(score)
                visited_words.append(current_word)
                message = "Valid and fancy."

            else:
                message = "Valid but not fancy."

            computer_word = comp_response_up(ending_letter_user)
            comp_word_meaning = self.get_meaning(computer_word)
            ending_letter_comp = computer_word[-1]
            all_comp_words.append(computer_word)

            return message, computer_word, ending_letter_comp, comp_word_meaning, right_word

        return "Invalid word.", "NA", "NA", "NA", False

class GameOverView(View):
    template_name = 'game_over.html'

    def get(self, request):
        return render(request, self.template_name)



# all_comp_words = [] 
# visited_words = set()

# def get_meaning(word):

#     req = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + word
#     data = json.loads(requests.get(req).text)
#     if len(data) == 1:
#         meaning = data[0]['meanings'][0]['definitions'][0]['definition']
#     else:
#         meaning = "Definition not available."
#     return meaning

# def home(request):
    
#     if request.method == 'GET':
#         print("GET request")
#         request.session['score'] = 0
#     right_word = True
#     score = request.session.get('score', 0)

#     if request.META.get('HTTP_CACHE_CONTROL') == 'max-age=0':
#         #all_comp_words = []
#         pass

#     if request.method == 'POST':
#         try:
#             current_word = request.POST.get('current_word', '')
#             current_word = re.sub(r"\s+", "", current_word)
#             if len(current_word) > 0:
#                 ending_letter_user = current_word[-1]

#                 message = "default messsage"
#                 print("Entered word is: ", current_word)
#                 print(is_valid_word(current_word))
#                 if is_valid_word(current_word):
#                     print(len(all_comp_words))
#                     if len(all_comp_words) > 0:
#                         print("Entered")
#                         ending_letter_comp = all_comp_words[-1][-1]
#                         print(f"Last computer word: {all_comp_words[-1]}")
#                         if current_word[0] != ending_letter_comp:
#                             message = f"Word should begin with the letter: {ending_letter_comp}"
#                             right_word = False

#                     if is_fancy_word(current_word) and right_word:
#                         if current_word in visited_words:
#                             print("Repeated")
#                             message = f"{current_word} has already been used."
#                         else:
#                             message = "Valid and fancy"
#                             score += 1
#                             visited_words.add(current_word)
#                     else:
#                         if right_word:
#                             message = "Valid but not fancy"
#                         request.session['score'] = 0
#                         score = 0
#                         visited_words.add(current_word)

#                 else:
#                     message = "invalid"
#                     score = 0
#                     request.session['score'] = 0
                    
#                 computer_word = comp_response_up(ending_letter_user)
#                 comp_word_meaning = get_meaning(computer_word)
#                 ending_letter_comp = computer_word[-1]
#                 all_comp_words.append(computer_word) 

#             else:
#                 message = "Input is blank."
#                 score = 0
#                 request.session['score'] = 0
#                 ending_letter_user = "NA"
#                 ending_letter_comp = "NA"
#                 comp_word_meaning = "NA"
#                 computer_word = "NA"


#             request.session['score'] = score
#             return render(request, 'home.html', {'score': score, 'comp_word_meaning': comp_word_meaning, 'ending_letter':ending_letter_comp, 'computer_word':computer_word,'message':message, 'all_comp_words':all_comp_words})

#         except KeyError:
#             request.session['score'] = 0
#             score = 0
#             message = "No input found."
        
#     else:
#         request.session['score'] = 0
#         score = 0
#         message = "Welcome to the game!"
#         # ending_letter = all_comp_words[-1][-1]
#         # computer_word = all_comp_words[-1]
#         message = "Enter your first word!"
#         return render(request, 'home.html', {'score': score, 'ending_letter':"NA", 'computer_word':"NA",'message':message, 'all_comp_words':[]})

# def game_over(request):

#     return render(request, 'game_over.html')