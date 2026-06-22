import socketio
import asyncio

client = socketio.AsyncClient()
server_ip = "127.0.0.1:5000"
async def main():
    await client.connect(f'http://{server_ip}', auth={
        'username': 'Khun'
    })

    client.on('new_message', print)

    menu = (
    "Hello to Superbuzzer quizz dear friend !\n"
    "I'm Corentin, best presentator of Belgium.\n"
    "I'm assisted by Jerome who's still currently studying the code of this application !\n\n"
    "What do you want to do ?\n\n"
    "\t 1. Create a party room\n"
    "\t 2. Join a party room\n"
    "\t 3. Drink a beer\n\n"
    "Please enter your choice [1-3] : "
    )
    
    message = await asyncio.to_thread(input, menu)
    print(message)
    if message == "1":
        await client.emit('start_game', {})
    elif message == "2":
        pass
    elif message == "3":
        print("Sorry, Jerome drank all my stock of beers during last weekend.")

    await client.wait()


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