import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 60000, // 60초로 증가 (POST 요청 처리 시간이 오래 걸림)
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 추가
instance.interceptors.request.use(
  (config) => {
    console.log('API 요청:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API 요청 에러:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 추가
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API 응답 에러:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export default instance;
