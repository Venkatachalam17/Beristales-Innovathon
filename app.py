# app.py
from flask import Flask, render_template, request, jsonify
import random
from tutor_words import letter_words

app = Flask(__name__)

# Practice sentences (4 pangrams)
practice_sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "Pack my box with five dozen liquor jugs.",
    "Sphinx of black quartz, judge my vow.",
    "How quickly daft jumping zebras vex."
]

# Final assessment sentences
assessment_sentences = [
    "Jackdaws love my big sphinx of quartz.",
    "The five boxing wizards jump quickly.",
    "How vexingly quick daft zebras jump.",
    "Bright vixens jump; dozy fowl quack."
]

@app.route('/')
def home():
    return render_template('touch.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    typed = data.get('typed', '')
    expected = data.get('expected', '')
    mistakes = {}

    # Count mistakes per letter
    for t_char, e_char in zip(typed, expected):
        if t_char != e_char:
            mistakes[e_char.lower()] = mistakes.get(e_char.lower(), 0) + 1

    # Extra/missing letters
    if len(expected) > len(typed):
        for c in expected[len(typed):]:
            mistakes[c.lower()] = mistakes.get(c.lower(), 0) + 1
    elif len(typed) > len(expected):
        for c in typed[len(expected):]:
            mistakes[c.lower()] = mistakes.get(c.lower(), 0) + 1

    total_keys = max(len(expected), len(typed))
    correct_chars = total_keys - sum(mistakes.values())
    acc = round((correct_chars / total_keys) * 100) if total_keys > 0 else 0

    feedback = f"You completed the sentence! Accuracy: {acc}%"
    suggestions = [{"letter": k, "count": v} for k, v in mistakes.items()]

    return jsonify({"feedback": feedback, "suggestions": suggestions, "mistakes": mistakes, "accuracy": acc})

@app.route('/tutor_words', methods=['POST'])
def tutor_words():
    data = request.get_json()
    mistakes = data.get('mistakes', {})
    words_to_practice = []

    # Sort letters by frequency
    sorted_letters = sorted(mistakes.items(), key=lambda x: x[1], reverse=True)
    for letter, _ in sorted_letters:
        if letter in letter_words:
            words_to_practice.extend(letter_words[letter])

    random.shuffle(words_to_practice)
    return jsonify({"words": words_to_practice[:20]})

@app.route('/assessment', methods=['GET'])
def assessment():
    sentence = random.choice(assessment_sentences)
    return jsonify({"sentence": sentence})

if __name__ == '__main__':
    app.run(debug=True)
