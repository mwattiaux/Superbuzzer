import { useNavigate } from "react-router-dom";
import { useState } from "react";

function Home() {
    const [room, setRoom] = useState("");
    const navigate = useNavigate();

    return (
        <>
            <h1>Super Buzzer</h1>
            <input
                placeholder="Nom de la room"
                value={room}
                onChange={(e) => setRoom(e.target.value)}
            />

            <button onClick={() => navigate("/" + room)}>
                Rejoindre
            </button>
        </>
    );
}

export default Home;