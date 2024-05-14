from flask import Flask, render_template, request, redirect
import redis
import json
import pika

app = Flask(__name__)
redis_db = redis.StrictRedis(host='host.docker.internal', port=6379, db=0, decode_responses=True)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
channel = connection.channel()
channel.queue_declare(queue='scrape_task_queue', durable=True)


def get_newest_prices():
    all_prices_keys = redis_db.keys("all_prices:*")
    all_prices_keys.sort(reverse=True)
    newest_prices_key = all_prices_keys[0] if all_prices_keys else None
    
    if newest_prices_key:
        newest_prices = redis_db.smembers(newest_prices_key)
        return newest_prices
    else:
        return set() 


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    keyword = request.form['keyword']
    num_pages = request.form['num_pages']

    data = {'keyword': keyword, 'num_pages': num_pages}
    channel.basic_publish(exchange='',
                          routing_key='scrape_task_queue',
                          body=json.dumps(data),
                          properties=pika.BasicProperties(delivery_mode=2))
    
    return redirect('/results')

@app.route('/results')
@app.route('/results')
def results():
    data = {}
    scraped_keys = redis_db.hkeys('scraped')
    for key in scraped_keys:
        data[key] = json.loads(redis_db.hget('scraped', key))
    newest_prices = list(get_newest_prices())  # Konwersja zbioru na listę
    return render_template('results.html', data=data, newest_prices=newest_prices)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
