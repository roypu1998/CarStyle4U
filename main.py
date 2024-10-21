from flask import Flask, render_template, request
from loads_cars_bot import thread, get_cars

app = Flask(__name__)

@app.route('/')
def index():
    size_filter = request.args.get('model', 'הכל')
    filtered_cars = [car for car in get_cars() if size_filter == 'הכל' or car['model'] == size_filter]
    options = [car['model'] for car in get_cars()]
    used = [set(options)]
    unique_opt = [x for x in used[0]]
    return render_template('index.html', cars=filtered_cars, options=unique_opt)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    car = next((car for car in get_cars() if car['id'] == car_id), None)
    if car is None:
        print(get_cars())
        return "Car not found", 404
    return render_template('car_detail.html', car=car)

@app.route('/about')
def contact():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)