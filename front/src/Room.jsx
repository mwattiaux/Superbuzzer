import { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { useParams } from "react-router-dom";

const socket = io("http://localhost:5001", {
  autoConnect: false,
});

function Room() {
  const { roomName } = useParams()
  const [username, setUsername] = useState("");
  const [connected, setConnected] = useState(false);

  const [question, setQuestion] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [results, setResults] = useState([]);
  const [answered, setAnswered] = useState(false)

  useEffect(() => {
    socket.on("connect", () => {
      console.log("Connected !");
    });

    socket.on("send_question", (data) => {
      setQuestion(data);
    });

    socket.on("time_left", (time) => {
      setTimeLeft(time);
    });

    socket.on("final_result", (data) => {
      setResults(data);
      setQuestion(null);
    });

    return () => {
      socket.off("connect");
      socket.off("send_question");
      socket.off("time_left");
      socket.off("final_result");
    };
  }, []);

  const connect = () => {
    socket.auth = { username };
    socket.connect();
    socket.emit("join_room", roomName);
    setConnected(true);
  };

  const startGame = () => {
    socket.emit("start_game", {});
  };

  const sendAnswer = (index) => {
    socket.emit("send_answer", index.toString());
    setAnswered(true)
  };

  if (!connected) {
    return (
      <div>
        <h1>Super Buzzer</h1>

        <input
          placeholder="Nom"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <button onClick={connect}>Se connecter</button>
      </div>
    );
  }

  return (
    <div>
      <h1>Super Buzzer</h1>

      <button onClick={startGame}>Start Game</button>

      <h3>Time left : {timeLeft}</h3>

      {question && (
        <div>
          <h2>{question.question}</h2>

          {question.choices.map((choice, index) => (
            <div key={index}>
              <button onClick={() => sendAnswer(index)}>
                {choice}
              </button>
            </div>
          ))}
        </div>
      )}

      {results.length > 0 && (
        <>
          <h2>Final ranking</h2>
          {results.map((player, index) => (
            <li key={index}>
            {player[0]} à {player[1]}
            </li>
          ))}
        </>
      )}
    </div>
  );
}

export default Room;