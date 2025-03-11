from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test  # ✅ Import auth decorators
import json
import os
import re
from docx import Document
from dictionary.models import Word, Paribhasha
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI

# ✅ Function to check if user is a superuser
def superuser_required(user):
    return user.is_superuser

@login_required  # ✅ Ensures only logged-in users can access this view
@user_passes_test(superuser_required)  # ✅ Ensures only superusers can access
def pb_delete_all(request):
    try:
        # Fetch all words from the database
        word_all = Word.objects.all()
        print(word_all.count())

        # Delete all words (which also deletes related Paribhasha records)
        word_all.delete()

        # Path to the JSON file
        json_file_path = os.path.join("media", "paribhasha_samhita.json")

        # Check if file exists, then delete it
        if os.path.exists(json_file_path):
            os.remove(json_file_path)

        return JsonResponse({"message": "All words deleted, JSON file removed."}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Deletion failed: {str(e)}"}, status=500)


@login_required  # ✅ Ensures only logged-in users can access this view
@user_passes_test(superuser_required)  # ✅ Ensures only superusers can access
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


@login_required  # ✅ Ensures only logged-in users can access this view
@user_passes_test(superuser_required)  # ✅ Ensures only superusers can access
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
        hindi_word = word

        # **Fetch Hinglish from Transliteration API**
        hinglish_translation = transliterate(hindi_word, DEVANAGARI, ITRANS).lower()

        # **Insert word into Word model**
        word_obj, created = Word.objects.get_or_create(
            hindi=hindi_word,
            defaults={"hinglish": hinglish_translation, "pageno": None}
        )

        # **Insert meanings into Paribhasha model, linking to Word**
        for meaning in meanings:
            Paribhasha.objects.create(word=word_obj, description=meaning)  # ✅ Fix: Changed `paribhasha` to `word`

        if created:
            inserted_count += 1  # Count newly added words

    return JsonResponse({"message": f"Data imported successfully! {inserted_count} new words added."}, status=200)

