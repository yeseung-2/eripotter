import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL, // .env.local에서 정의
  timeout: 60000, // 60초로 증가 (POST 요청 처리 시간이 오래 걸림)
});

export default instance;
