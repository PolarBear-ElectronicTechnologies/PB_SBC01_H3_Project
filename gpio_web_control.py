from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

GPIO = "15"
gpio_path = f"/sys/class/gpio/gpio{GPIO}/value"

if not os.path.exists(f"/sys/class/gpio/gpio{GPIO}"):
    with open("/sys/class/gpio/export", "w") as f:
        f.write(GPIO)
with open(f"/sys/class/gpio/gpio{GPIO}/direction", "w") as f:
    f.write("out")

HTML = '''
<!doctype html>
<title>GPIO Управление</title>
<h2>GPIO{{ pin }} — Управление</h2>
<form method="POST">
    <button name="state" value="1">Включить</button>
    <button name="state" value="0">Выключить</button>
</form>
<p>Текущее состояние: {{ state }}</p>
'''

@app.route("/", methods=["GET", "POST"])
def control():
    if request.method == "POST":
        state = request.form["state"]
        with open(gpio_path, "w") as f:
            f.write(state)
    with open(gpio_path, "r") as f:
        current = f.read().strip()
    return render_template_string(HTML, pin=GPIO, state=current)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)