import socketio
import uvicorn
import random
import json
from datetime import datetime
from generate_questions import generate_quiz

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*"
)
app = socketio.ASGIApp(sio)

question_file = 'questions/questions.json'
answered = None
clients = {}
current_question = None
rooms = set()


@sio.event
async def connect(sid, environ, auth):
    username = auth.get('username')
    print(f'The user {username} is connected')
    clients[sid] =  {"username" : username, "points" : 0}
    await sio.emit('available_rooms', list(rooms), to=sid)

@sio.event
async def disconnect(sid):
    username = clients.get(sid)
    print(f'The user {username} is disconnected')
    clients.pop(sid)

@sio.event
async def create_room(sid, room_name):
    if room_name:
        rooms.add(room_name)
        await join_room(sid, room_name)
        print(f"Room {room_name} created by {clients[sid]['username']}")
        await sio.emit('available_rooms', list(rooms))

@sio.event
async def join_room(sid, room):
    await sio.enter_room(sid, room=room)
    await sio.emit('server_message', f"User {clients[sid]['username']} joined room {room}", room=room)

@sio.event
async def exit_room(sid, room):
    await sio.leave_room(sid, room=room)
    await sio.emit('server_message', f"User {clients[sid]['username']} left room {room}", room=room)

@sio.on('start_game')
async def game_loop(sid, message):
    global rooms
    room = sio.rooms(sid)[1]
    questions = generate_quiz(2, "Random")
    print(questions)

    for question in questions['questions']:
        print(question)

        await send_question(question, room)
        waiting_time = 10
        for i in range(waiting_time):
            await sio.emit("time_left", waiting_time-i, room=room)
            await sio.sleep(1)
            
        print("\rTemps écoulé !                  ")

    package = []
    list_of_ids = sio.manager.get_participants(namespace="/", room=room)
    for item in list_of_ids:
        player_sid = item[0]
        package.append((clients[player_sid]['username'], clients[player_sid]['points']))
    package.sort(key= lambda x: x[1], reverse=True)

    await sio.emit('final_result', package, room=room)
    await sio.close_room(room)
    rooms.discard(room)





# custom events
@sio.on('send_message')
async def send_message(sid, data):
    username = clients.get(sid)
    print(f'The user {username} emit a new message')
    await sio.emit('new_message', data|{
        'username': username,
        'date': str(datetime.now())
    })

# def load_questions(number_of_question: int):
#     try:
#         questions = []
#         with open(question_file, 'r') as file:
#             data = json.load(file)
#         seen = set()
#         max_question = int(list(data.keys())[-1])
#         while len(questions) < number_of_question:
#             question_number = random.randint(1,max_question)
#             while question_number in seen:
#                 question_number = random.randint(1,max_question)
#             seen.add(question_number)
#             data[f"{question_number}"]["choices"] = list(set(data[f"{question_number}"]["choices"]))
#             questions.append(data[f"{question_number}"])
#         return questions
            
#     except FileNotFoundError:
#         print(f"Error: The file '{question_file} was not found.")


 
def answer_checker(question, answer):
    print(f'Answer : {answer}')
    print(question)
    print(f'Index : {str(question["choices"].index(question["valid"]))}')
    return answer == str(question["choices"].index(question["valid"]))
   

async def send_question(question, room):
    global answered, current_question

    current_question = question

    answered = None
    payload = {
        "question": question["question"],
        "choices": question["choices"]
    }

    print(f'Envoi de la question : {payload}')
    await sio.emit("send_question", payload, room=room)
        
@sio.on("send_answer")
async def answer_receiver(user_id, user_answer):
    global answered, current_question

    
    if answer_checker(current_question, user_answer) and not answered:
        clients[user_id]["points"] += 1
        answered = user_id
    
    sio.emit("result", {'status': clients[user_id]['points']}, to=user_id)
    


if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=5001)