import socketio
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

client = socketio.AsyncClient()
server_url = f"{os.getenv("server_ip")}:{os.getenv("server_port")}"
roomlist = []

async def main():
    await client.connect(f'http://{server_url}', auth={
        'username': 'BMmaster'
    })

    client.on('new_message', print)

    
    valid_input = False
    while not valid_input:
        match await asyncio.to_thread(input,"1: create a room\n2: Join a room\n"):
            case "1":
                valid_input = True
                room_name = None
                while not room_name:
                    room_name = await asyncio.to_thread(input,"Room name: ")
                await client.emit('create_room', room_name)
            case "2":
                if roomlist:
                    valid_input = True
                    room_name = None
                    while not (room_name in roomlist):
                        room_name = await asyncio.to_thread(input,"Room name: ")
                    await client.emit('join_room', room_name)
                else:
                    print("No room available")
            case __:
                await print("Enter a valid input")
    if await asyncio.to_thread(input) == "start":
        await client.emit('start_game', {})

    await client.wait()


@client.on('message')
async def show_message(message):
    print(f"###  {message}")

@client.on('available_rooms')
async def on_available_rooms(rooms):
    global roomlist
    roomlist = rooms
    print(f"\n### Available Rooms #")
    if not rooms:
        print("No rooms")
    else:
        for room in rooms:
            print(f"-- {room}")
    print("========================\n")

@client.on("send_question")
async def show_question(question):
    print("\n" + "-"*30)
    print(f"QUESTION : {question["question"]}")
    print("-"*30)
    
    for i, choice in enumerate(question["choices"]):
        print(f"{i}. {choice}")
        
    print("-"*30)

    answer = await asyncio.to_thread(input,"Answer : ")

    await client.emit('send_answer', answer)

@client.on("final_result")
async def show_final_results(package):
    print("\n" + "-"*30)
    print("-------- FINAL RESULT -------")
    print("-"*30 + "\n")
    for index, user_stats in enumerate(package):
        username = user_stats[0]
        user_points = user_stats[1]
        print(f"{index+1}. {username} - {user_points} points")
    print(package)
    print("\n" + "-"*30)

@client.on("time_left")
async def show_time_left(time: str):
    print(f"\rTime left : {time} seconds\n", end="", flush=True)

if __name__ == '__main__':
    asyncio.run(main())