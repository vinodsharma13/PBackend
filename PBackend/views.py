from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from docx import Document
import os
import re  # Import regex for additional cleanup

from dictionary.models import Paribhasha, ParibhashaLine


from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI

def pb_delete_all(request):
    try:
        # Fetch the word from the database
        paribhasha_all = Paribhasha.objects.all()
        print(paribhasha_all.count)
        paribhasha_all.delete()


        return JsonResponse({"paribhasha": "Deleted all"}, status=200)

    except Paribhasha.DoesNotExist:
        return JsonResponse({"error": "Not Deleted"}, status=404)


# def get_hinglish_google(request):
#     translator = Translator()
#     hindi_word="अखण्ड"
#     try:
#         # Fetch the word from the database
#         paribhasha_obj = Paribhasha.objects.get(hindi=hindi_word)

#         # If Hinglish is not saved in the database, generate it dynamically
#         if not paribhasha_obj.hinglish:
#             hinglish_translation = translator.translate(hindi_word, src="hi", dest="en").text  # Google Translate API
#             paribhasha_obj.hinglish = hinglish_translation  # Update model

#             paribhasha_obj.save()  # Save updated Hinglish field

#         return JsonResponse({"hindi": hindi_word, "hinglish": paribhasha_obj.hinglish}, status=200)

#     except Paribhasha.DoesNotExist:
#         return JsonResponse({"error": "Word not found in database"}, status=404)


@csrf_exempt
def ip_json(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        try:
            doc = Document(uploaded_file)
        except Exception as e:
            return JsonResponse({"error": f"Invalid DOCX file: {str(e)}"}, status=400)

        word_dict = {}
        current_word = None  # Store the current word being processed

        # Regex pattern to match section headers (like "ई", "उ") to ignore
        section_header_pattern = re.compile(r"^[\u0900-\u097F]$")

        # Process each paragraph in the document
        for para in doc.paragraphs:
            line = para.text.strip()
            if not line:
                continue  # Skip empty lines

            # Remove unnecessary tab characters and multiple spaces
            line = re.sub(r"\t+", " ", line)
            line = re.sub(r"\s{2,}", " ", line)  # Remove extra spaces

            # Check if line is a section header (single letter headers like "ई", "उ")
            if section_header_pattern.fullmatch(line):
                current_word = None  # Reset current word to avoid adding this as a meaning
                continue  # Skip section header

            # Check if the line contains a word and its meaning (format: "word - meaning")
            if " - " in line:
                parts = line.split(" - ", 1)  # Split only at the first occurrence of " - "
                new_word = parts[0].strip()  # Extract the word
                meaning = parts[1].strip()  # Extract the first meaning

                if new_word:
                    current_word = new_word  # Set this as the new current word
                    word_dict[current_word] = [meaning]  # Start a new list of meanings
            elif current_word:
                # Additional meanings (lines that start with "-")
                clean_meaning = re.sub(r"^-\s*", "", line)  # Remove leading "- "
                if clean_meaning:
                    word_dict[current_word].append(clean_meaning)
                else:
                    current_word = None  # Reset if a new word is expected

        # Save JSON output to a file
        output_path = os.path.join("media", "paribhasha_samhita.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(word_dict, json_file, ensure_ascii=False, indent=4)

        return JsonResponse({
            "message": "File processed successfully!",
            "json_path": output_path,
            "data": word_dict
        }, status=200)

    return render(request, "upload.html")  # Render the file upload form



# from indic_transliteration.sanscript import transliterate, HK
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI


@csrf_exempt
def ip_models(request):
    # Load JSON file from media directory
    json_path = os.path.join("media", "paribhasha_samhita.json")

    if not os.path.exists(json_path):
        return JsonResponse({"error": "JSON file not found. Please upload first."}, status=400)

    try:
        with open(json_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load JSON data
    except Exception as e:
        return JsonResponse({"error": f"Error reading JSON file: {str(e)}"}, status=400)

    inserted_count = 0  # Track inserted words


    for word, meanings in data.items():

        # Insert word into Paribhasha model (if not exists)
        hindi_word=word

        # hinglish_translation = translator.translate(hindi_word, src="hi", dest="en").text  # Google Translate API

        # Convert Hindi word to Hinglish (ITRANS gives readable Hinglish)
        # hinglish_translation = transliterate(hindi_word, DEVANAGARI, ITRANS).lower()
         # **Fetch Hinglish from Google Transliteration API**
        hinglish_translation = get_hinglish_from_itran(hindi_word)

        # Insert word into Paribhasha model
        paribhasha_obj, created = Paribhasha.objects.get_or_create(
            hindi=hindi_word,
            defaults={"hinglish": hinglish_translation, "pageno": None}
        )
        # Insert meanings into ParibhashaLine model, linking to Paribhasha
        for meaning in meanings:
            ParibhashaLine.objects.create(paribhasha=paribhasha_obj, name=meaning)

        if created:
            inserted_count += 1  # Count newly added words

    return JsonResponse({"message": f"Data imported successfully! {inserted_count} new words added."}, status=200)




def get_hinglish_from_itran(hindi_text):
    try:
        hinglish_translation = transliterate(hindi_text, DEVANAGARI, ITRANS)
        return hinglish_translation.lower()
    except Exception as e:
        print(f"Error: {e}")
        return hindi_text  # Fallback in case of failure
