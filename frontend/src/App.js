import React, { useState, useEffect } from 'react';
import { initializeGame, chatWithGPT, getHint, checkAnswer, giveUp } from './api';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [hint, setHint] = useState('');

  // ゲーム初期化
  const startGame = async () => {
    try {
      const message = await initializeGame();
      setMessages([{ role: 'assistant', content: message }]);
      setHint('');
      setInput('');
    } catch (error) {
      console.error('Error initializing the game:', error);
    }
  };

  useEffect(() => {
    startGame();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    setMessages([...messages, { role: 'user', content: input }]);
    setLoading(true);

    try {
      const response = await chatWithGPT(input);
      setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      console.error('Error chatting with GPT:', error);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const handleCheckAnswer = async () => {
    if (!input.trim()) return;

    setLoading(true);
    try {
      const result = await checkAnswer(input);
      setMessages((prev) => [...prev, { role: 'assistant', content: result }]);
    } catch (error) {
      console.error('Error checking answer:', error);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const fetchHint = async (level) => {
    try {
      const hintResponse = await getHint(level);
      setHint(hintResponse);
    } catch (error) {
      console.error('Error fetching hint:', error);
      setHint('エラー: ヒントを取得できませんでした。');
    }
  };

  const handleGiveUp = async () => {
    try {
      const result = await giveUp();
      setMessages((prev) => [...prev, { role: 'assistant', content: result }]);
      setHint(''); // ヒントをリセット
    } catch (error) {
      console.error('Error giving up:', error);
    }
  };

  return (
    <div>
      <h1>Akinator Game</h1>
      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ margin: '10px 0' }}>
            <strong>{msg.role === 'user' ? 'You' : 'Akinator'}:</strong> {msg.content}
          </div>
        ))}
        {hint && <div style={{ marginTop: '20px', color: 'blue' }}>ヒント: {hint}</div>}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={loading}
      />
      <button onClick={handleSend} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
      <button onClick={handleCheckAnswer} disabled={loading}>
        答えを確認する
      </button>
      <button onClick={handleGiveUp} disabled={loading}>
        ギブアップ
      </button>
      <button onClick={startGame} disabled={loading}>
        新しいゲーム
      </button>
      <div style={{ marginTop: '20px' }}>
        <button onClick={() => fetchHint('easy')}>簡単なヒント</button>
        <button onClick={() => fetchHint('medium')}>普通のヒント</button>
        <button onClick={() => fetchHint('hard')}>難しいヒント</button>
      </div>
    </div>
  );
}

export default App;