import redis
from flask import Flask, render_template, request

app = Flask(__name__)

# Połączenie z Redis
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

# Lista dostępnych filmów i początkowa liczba miejsc
movies = ["Film A", "Film B", "Film C"]

# Mapowanie filmów na obrazki
movie_images = {
    "Film A": "https://via.placeholder.com/300x200/0000FF/FFFFFF?text=Film+A",
    "Film B": "https://via.placeholder.com/300x200/FF0000/FFFFFF?text=Film+B",
    "Film C": "https://via.placeholder.com/300x200/008000/FFFFFF?text=Film+C"
}

# Ustawienie początkowej liczby miejsc w Redis
for movie in movies:
    if not redis_client.exists(movie):
        redis_client.set(movie, 50)

@app.route('/', methods=['GET', 'POST'])
def reserve():
    message = None
    if request.method == 'POST':
        movie = request.form['movie']
        seats_left = int(redis_client.get(movie))

        if seats_left > 0:
            redis_client.decr(movie)
            message = f"✅ Zarezerwowano miejsce na {movie}!"
        else:
            message = "❌ Brak miejsc!"

    return render_template('index.html', seats={m: redis_client.get(m) for m in movies}, 
                           movie_images=movie_images, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
