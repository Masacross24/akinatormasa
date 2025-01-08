import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ゲームの初期化
export const initializeGame = async () => {
  try {
    const response = await api.post('/initialize');
    return response.data.message;
  } catch (error) {
    console.error('Error initializing game:', error);
    throw error;
  }
};

// チャットメッセージの送信
export const chatWithGPT = async (message) => {
  try {
    const response = await api.post('/chat', { message });
    return response.data.response;
  } catch (error) {
    console.error('Error chatting with GPT:', error);
    throw error;
  }
};

// ヒントの取得
export const getHint = async (level) => {
  try {
    const response = await api.post('/hint', { level });
    return response.data.hint;
  } catch (error) {
    console.error('Error fetching hint:', error);
    throw error;
  }
};

// 正解のチェック
export const checkAnswer = async (answer) => {
  try {
    const response = await api.post('/check', { answer });
    return response.data.result;
  } catch (error) {
    console.error('Error checking answer:', error);
    throw error;
  }
};

// ギブアップ
export const giveUp = async () => {
  try {
    const response = await api.post('/give_up');
    return response.data.result;
  } catch (error) {
    console.error('Error giving up:', error);
    throw error;
  }
};
