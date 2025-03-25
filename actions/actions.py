from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
import requests
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from googletrans import Translator

# Load KCC dataset
kcc_df = pd.read_csv("cleaned_AP_dataset.csv", encoding="ISO-8859-1")  # Use this instead of UTF-8

# Preprocess dataset: Convert to lowercase and handle NaN values
kcc_df["QueryText"] = kcc_df["QueryText"].astype(str).str.lower().fillna("")
kcc_df["KccAns"] = kcc_df["KccAns"].astype(str).fillna("No information available.")

# TF-IDF Vectorizer for text similarity
#vectorizer = TfidfVectorizer()
vectorizer = TfidfVectorizer(ngram_range=(1, 3))  # Capture more word combinations
query_vectors = vectorizer.fit_transform(kcc_df["QueryText"])

translator = Translator()


def translate_to_telugu(text: str) -> str:
    """Translates English text to Telugu."""
    try:
        translation = translator.translate(text, src='en', dest='te')
        return translation.text
    except Exception as e:
        return "(Translation unavailable) " + text


def find_best_match(user_query: str) -> str:
    """
    Finds the best-matching answer for a user query using TF-IDF and fuzzy matching.
    """
    # Step 1: Use TF-IDF similarity
    user_vector = vectorizer.transform([user_query])
    similarities = cosine_similarity(user_vector, query_vectors)

    best_match_index = np.argmax(similarities)
    best_match_score = similarities[0, best_match_index]

    # Step 2: If TF-IDF confidence is low, use fuzzy matching
    if best_match_score < 0.5:  # Increase confidence threshold
        max_fuzz_score = 0
        best_fuzz_match = None

        for idx, text in enumerate(kcc_df["QueryText"]):
            fuzz_score = fuzz.partial_ratio(user_query, text)
            if fuzz_score > max_fuzz_score:
                max_fuzz_score = fuzz_score
                best_fuzz_match = idx

        if max_fuzz_score > 50:  # Lower fuzzy match threshold
            best_match_index = best_fuzz_match

    return kcc_df.iloc[best_match_index]["KccAns"]


# Action for Agriculture Information
class ActionFetchAgricultureInfo(Action):
    def name(self) -> Text:
        return "action_fetch_agriculture_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
        Dict[Text, Any]]:
        user_query = tracker.latest_message.get("text", "").lower().strip()

        if not user_query:
            dispatcher.utter_message(text="I couldn't understand your query. Please ask again.")
            return []

        answer = find_best_match(user_query)
        telugu_answer = translate_to_telugu(answer)

        response_message = f"English: {answer}\nTelugu: {telugu_answer}"
        dispatcher.utter_message(text=response_message)

        return []

import os

class ActionFetchWeatherInfo(Action):
    def name(self) -> Text:
        return "action_fetch_weather_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = next(tracker.get_latest_entity_values("location"), None)

        if location:
            api_key = os.getenv("WEATHER_API_KEY")  # Get API key from environment variable
            if not api_key:
                dispatcher.utter_message(text="Weather API key is missing! Please check the server settings.")
                return []

            url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                temp = data['main']['temp']
                weather_desc = data['weather'][0]['description']
                message = f"The current temperature in {location} is {temp}°C with {weather_desc}."
            else:
                message = "Sorry, I couldn't fetch the weather details. Please try again later."
        else:
            message = "Please provide a location to fetch weather information."

        dispatcher.utter_message(text=message)
        return []

class ActionFetchHorticultureInfo(Action):
    def name(self) -> Text:
        return "action_fetch_horticulture_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        crop = next(tracker.get_latest_entity_values("fruit"), None) or next(
            tracker.get_latest_entity_values("vegetable"), None)
        if not crop:
            dispatcher.utter_message(text="Please specify a fruit or vegetable for horticulture information.")
            return []
        crop = crop.lower()
        user_query = f"{crop} {tracker.latest_message.get('text').lower()}"
        answer = find_best_match(user_query)
        telugu_answer = translate_to_telugu(answer)
        dispatcher.utter_message(text=f"English: {answer}\nTelugu: {telugu_answer}")
        return []


class ActionFetchCropRecommendation(Action):
    def name(self) -> Text:
        return "action_fetch_crop_recommendation_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
        Dict[Text, Any]]:
        user_query = tracker.latest_message.get("text", "").strip().lower()
        if not user_query:
            dispatcher.utter_message(text="I couldn't understand your query. Please ask again.")
            return []
        answer = find_best_match(user_query)
        telugu_answer = translate_to_telugu(answer)
        dispatcher.utter_message(text=f"English: {answer}\nTelugu: {telugu_answer}")
        return []


class ActionFetchSoilRecommendation(Action):
    def name(self) -> Text:
        return "action_fetch_soil_recommendation"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
        Dict[Text, Any]]:
        user_query = tracker.latest_message.get("text", "").strip().lower()
        if not user_query:
            dispatcher.utter_message(text="I couldn't understand your query. Please ask again.")
            return []
        answer = find_best_match(user_query)
        telugu_answer = translate_to_telugu(answer)
        dispatcher.utter_message(text=f"English: {answer}\nTelugu: {telugu_answer}")
        return []

class ActionFallback(Action):
    def name(self) -> Text:
        return "action_fallback"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = "I'm sorry, but I couldn't find relevant information for your query. Please try rephrasing your question or ask something else."
        telugu_message = translate_to_telugu(message)
        dispatcher.utter_message(text=f"English: {message}\nTelugu: {telugu_message}")
        return []
