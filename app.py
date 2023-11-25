from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

events = [{'id': 1, 'name': 'takshak', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'Seminar hall 2'}, {'id': 2, 'name': 'sanskriti', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'ootpra'}, {'id': 3, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 4, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 5, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 6, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}]

@app.route('/')
def home():
    return render_template('home.html', events=events)

@app.route('/events/<int:event_id>')
def event(event_id):
    specific_event = next((event for event in events if event['id'] == event_id), None)
    if specific_event:
        return render_template('event.html', event=specific_event)
    else:
        return "Event not found", 404
if __name__ == "__main__":
    app.run(debug=True)