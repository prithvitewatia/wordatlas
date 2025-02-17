from django.shortcuts import render
from django.views import View
import os 
import json 
import re
import requests 
from .models import Bookmark
from . word_utils import is_valid_word, is_fancy_word, comp_response_up
from django.urls import reverse_lazy 
from .forms import RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, FormView
from rest_framework import viewsets
from .models import Bookmark
from .serializers import BookmarkSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Login View
class LoginView(LoginView):
    template_name = 'login.html'

class MyAuthenticatedView(LoginRequiredMixin, TemplateView):
    template_name = 'authenticated_template.html'

# Register View
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):

        return super().form_invalid(form)


# Home View

class HomeView(LoginRequiredMixin, View):

    # Fetch meaning of a word.
    @staticmethod
    def get_meaning(word):

        req = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + word
        data = json.loads(requests.get(req).text)
        if len(data) == 1:
            meaning = data[0]['meanings'][0]['definitions'][0]['definition']
        else:
            meaning = "Definition not available."
        return meaning

    # Remove trailing spaces.
    def process_word(self, current_word):
        return re.sub(r"\s+", "", current_word)

    def handle_word_logic(self, current_word, score, all_comp_words, visited_words):

        if len(current_word) == 0:
            message = "Input is blank."
            return "Input is blank.", "NA", "NA", "NA", False

        right_word = True 
        ending_letter_user = current_word[-1]
        if is_valid_word(current_word):
            if all_comp_words:
                ending_letter_comp = all_comp_words[-1][-1]
            else:
                ending_letter_comp = "NA"
            if current_word[0] != ending_letter_comp and visited_words:
                message = f"Word should begin with the letter: {ending_letter_comp}"
                right_word = False
                score = 0

            if is_fancy_word(current_word) and right_word:
                if current_word in visited_words:
                    message = f"{current_word} has already been used."
                    score = 0

                else:
                    message = "Valid and fancy."
                    score += 1
                    visited_words.append(current_word)

            else:

                if right_word:
                    message = "Valid but not fancy."
                
                score = 0
                visited_words.append(current_word)
        else:
            message = "Invalid word."
            score = 0
             

        computer_word = comp_response_up(ending_letter_user)
        comp_word_meaning = self.get_meaning(computer_word)
        ending_letter_comp = computer_word[-1]
        all_comp_words.append(computer_word) 

        return computer_word, comp_word_meaning, all_comp_words, score, message, visited_words


        

    def get(self, request, *args, **kwargs):
        template_name = 'home.html'
        if 'score' not in request.session:
            self.request.session.setdefault('score', 0)
            self.request.session.setdefault('visited_words', [])
            self.request.session.setdefault('all_comp_words', [])
        context = {'score': 0, 'ending_letter': "NA", 'computer_word': "NA", 'message': "Enter your first word!", 'all_comp_words': []}
        return render(request, template_name, context)


    
    def bookmark(self, word, user):
        meaning = self.get_meaning(word)    
        Bookmark.objects.create(user=user, word=word, meaning=meaning)

    def post(self, request, *args, **kwargs):

        print("Entered post.")
        
        current_word = request.POST.get('current_word', '')
        current_word = self.process_word(current_word)
        score = request.session.get('score', 0)
        print(f"Score fetched from session: {score}")
        visited_words = request.session.get('visited_words', [])
        print(f"Visited words: {visited_words}")
        all_comp_words = request.session.get('all_comp_words', [])
        computer_word, comp_word_meaning, all_comp_words, score, message, visited_words = self.handle_word_logic( current_word, score, all_comp_words, visited_words)
        request.session['computer_word'] = computer_word
        request.session['comp_word_meaning'] = comp_word_meaning
        request.session['all_comp_words'] = all_comp_words
        request.session['score'] = score
        request.session['message'] = message
        request.session['visited_words'] = visited_words 
        ending_letter_comp = computer_word[-1]
        return render(request, 'home.html', {'score': score, 'comp_word_meaning': comp_word_meaning, 'ending_letter':ending_letter_comp, 'computer_word':computer_word,'message':message, 'all_comp_words':all_comp_words})

    
# View to show when the player runs out of time.

class GameOverView(LoginRequiredMixin, View):
    template_name = 'game_over.html'

    def get(self, request):
        request.session['visited_words'] = []
        return render(request, self.template_name)



class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

# View to bookmark a word.

# class AddBookmark(LoginRequiredMixin, View):
#     def post(self, request):
#         word = request.POST.get('current_word', '')
#         meaning = get_meaning()