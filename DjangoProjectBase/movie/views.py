from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import openai
import os
from dotenv import load_dotenv, find_dotenv

from .models import Movie, Review

from .forms import ReviewForm, MovieRecommendation


def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm: 
        movies = Movie.objects.filter(title__icontains=searchTerm) 
    else: 
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': movies})


def about(request):
    return render(request, 'about.html')


def detail(request, movie_id):
    movie = get_object_or_404(Movie,pk=movie_id)
    reviews = Review.objects.filter(movie = movie)
    return render(request, 'detail.html',{'movie':movie, 'reviews': reviews})


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]


def recomendations(request):
    movie = None
    error = None
    
    if request.method == 'POST':
        form = MovieRecommendation(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            
            _ = load_dotenv('../openAI.env')
            openai.api_key  = os.environ['openAI_api_key']
            
            prompt_final = f"{prompt}. Solo escribe el titulo y absolutamente nada mas"
            
            response = get_completion(prompt_final)
            
            
            try: 
                movie_recommendation = Movie.objects.get(title=response)
                movie = movie_recommendation
                print(movie)
            except Movie.DoesNotExist:
                movie = None
                error = "No se encontró ninguna película que coincida con la peticion."
    
    else:
        form = MovieRecommendation()
    
    return render(request, 'recomendations.html',  {'form': form, 'movie': movie, 'error': error})

@login_required
def createreview(request, movie_id):
    movie = get_object_or_404(Movie,pk=movie_id)
    if request.method == 'GET':
        return render(request, 'createreview.html',{'form':ReviewForm(), 'movie': movie})
    else:
        try:
            form = ReviewForm(request.POST)
            newReview = form.save(commit=False)
            newReview.user = request.user
            newReview.movie = movie
            newReview.save()
            return redirect('detail', newReview.movie.id)
        except ValueError:
            return render(request, 'createreview.html',{'form':ReviewForm(),'error':'bad data passed in'})

@login_required       
def updatereview(request, review_id):
    review = get_object_or_404(Review,pk=review_id,user=request.user)
    if request.method =='GET':
        form = ReviewForm(instance=review)
        return render(request, 'updatereview.html',{'review': review,'form':form})
    else:
        try:
            form = ReviewForm(request.POST, instance=review)
            form.save()
            return redirect('detail', review.movie.id)
        except ValueError:
            return render(request, 'updatereview.html',{'review': review,'form':form,'error':'Bad data in form'})
        
@login_required
def deletereview(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    review.delete()
    return redirect('detail', review.movie.id)