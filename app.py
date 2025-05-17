from flask import Flask, render_template, request
import pickle
import numpy as np

# Load precomputed data once at startup
with open('popular.pkl', 'rb') as f:
    popular_df = pickle.load(f)
with open('pt.pkl', 'rb') as f:
    pt = pickle.load(f)
with open('books.pkl', 'rb') as f:
    books = pickle.load(f)
with open('similarity_scores.pkl', 'rb') as f:
    similarity_scores = pickle.load(f)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template(
        'index.html',
        book_name=popular_df['Book-Title'].tolist(),
        author=popular_df['Book-Author'].tolist(),
        image=popular_df['Image-URL-M'].tolist(),
        votes=popular_df['num_ratings'].tolist(),
        rating=popular_df['avg_rating'].tolist()
    )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input', '').strip()

    # Handle missing or misspelled titles
    if user_input not in pt.index:
        return render_template(
            'recommend.html',
            error=f"Sorry, I couldn't find '{user_input}' in our catalogue."
        )

    idx = pt.index.get_loc(user_input)
    sim_scores = list(enumerate(similarity_scores[idx]))
    # get top 4 recommendations (skip the book itself at rank 0)
    top_similar = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:5]

    recommendations = []
    for book_idx, score in top_similar:
        title = pt.index[book_idx]
        entry = books[books['Book-Title'] == title].drop_duplicates('Book-Title').iloc[0]
        recommendations.append({
            'title': entry['Book-Title'],
            'author': entry['Book-Author'],
            'image': entry['Image-URL-M']
        })

    return render_template('recommend.html', recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug=True)
