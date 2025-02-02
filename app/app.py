import redis
from flask import Flask, render_template, request

app = Flask(__name__)

try:
    # Połączenie z Redis z obsługą błędów
    redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True, socket_timeout=5)
    redis_client.ping()  # Sprawdzenie, czy Redis działa
except redis.ConnectionError:
    redis_client = None
    print("❌ Błąd: Nie można połączyć się z Redis!")

# Lista dostępnych filmów i początkowa liczba miejsc
movies = ["Film A", "Film B", "Film C"]

# Ustawienie początkowej liczby miejsc w Redis
if redis_client:
    for movie in movies:
        if not redis_client.exists(movie):
            redis_client.set(movie, 50)

@app.route('/', methods=['GET', 'POST'])
def reserve():
    message = None

    if request.method == 'POST':
        movie = request.form.get('movie')

        if redis_client and movie in movies:
            seats_left = redis_client.get(movie)

            if seats_left is not None and seats_left.isdigit():
                seats_left = int(seats_left)

                if seats_left > 0:
                    redis_client.decr(movie)
                    message = f"✅ Zarezerwowano miejsce na {movie}!"
                else:
                    message = "❌ Brak miejsc!"
            else:
                message = "⚠️ Wystąpił błąd! Spróbuj ponownie."
        else:
            message = "❌ Niepoprawna rezerwacja!"

    return render_template('index.html', seats={m: redis_client.get(m) if redis_client else "Błąd" for m in movies}, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Włączony debug dla lokalnych testów
