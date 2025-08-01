import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL, // .env.local에서 정의
  timeout: 5000,
});

export default instance;
