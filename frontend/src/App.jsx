import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const App = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [fullTranscription, setFullTranscription] = useState('');
    const [chunkDuration, setChunkDuration] = useState(1000);

    // If you're running in local, you can use ws://localhost:8000/ws
    const [websocketUrl, setWebsocketUrl] = useState('ws://localhost:8000/ws');

    // If you're running in production, you can use wss://<your-domain>/ws
    // const [websocketUrl, setWebsocketUrl] = useState('wss://' + window.location.hostname + '/ws');

    const [buffer, setBuffer] = useState('');
    const recorderRef = useRef(null);
    const websocketRef = useRef(null);

    useEffect(() => {
        return () => {
            if (websocketRef.current) websocketRef.current.close();
        };
    }, []);

    const checkMicrophone = async () => {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const hasMicrophone = devices.some(device => device.kind === 'audioinput');
            if (!hasMicrophone) {
                alert('No microphone detected');
            }
        } catch (error) {
            alert('Error checking for microphone: ' + error.message);
        }
    };

    const setupWebSocket = () => {
        websocketRef.current = new WebSocket(websocketUrl);
        websocketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setFullTranscription((prev) => prev + data.transcription);
            setBuffer(data.buffer);
        };

        websocketRef.current.onerror = () => {
            stopRecording();
            alert('Error connecting to WebSocket');
        };
    };

    const startRecording = async () => {
        await checkMicrophone();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        recorderRef.current.ondataavailable = (e) => {
            if (websocketRef.current) {
                // websocketRef.current.send(e.data);
                websocketRef.current.send("test");
            }
        };
        recorderRef.current.start(chunkDuration);
        setIsRecording(true);
    };

    const stopRecording = () => {
        if (recorderRef.current) {
            recorderRef.current.stop();
            recorderRef.current = null;
        }
        if (websocketRef.current) {
            websocketRef.current.close();
            websocketRef.current = null;
        }
        setIsRecording(false);
    };

    const toggleRecording = async () => {
        if (isRecording) {
            stopRecording();
        } else {
            setupWebSocket();
            await startRecording();
        }
    };

    return (
        <div className="container">
            <div className="settings-container">
                <button
                    className={`record-button ${isRecording ? 'recording' : ''}`}
                    onClick={toggleRecording}
                >
                    🎙️
                </button>
                <div className="settings">
                    <label>
                        Chunk size (ms):
                        <select
                            value={chunkDuration}
                            onChange={(e) => setChunkDuration(parseInt(e.target.value))}
                        >
                            {[500, 1000, 2000, 3000, 4000, 5000].map((value) => (
                                <option key={value} value={value}>{value} ms</option>
                            ))}
                        </select>
                    </label>
                    {/* <label>
                        WebSocket URL:
                        <input
                            type="text"
                            value={websocketUrl}
                            onChange={(e) => setWebsocketUrl(e.target.value)}
                        />
                    </label> */}
                </div>
            </div>
            <p>{isRecording ? 'Recording...' : 'Click to start transcription'}</p>
            <div className="transcriptions">
                <span className="transcription">{fullTranscription}</span>
                <span className="buffer">{buffer}</span>
            </div>
        </div>
    );
};

export default App;
