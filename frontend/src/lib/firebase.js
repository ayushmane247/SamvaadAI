import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBcqtKWikQRf93miv9aE_r4TuYutkUJBeQ",
  authDomain: "samvaadai-7f99a.firebaseapp.com",
  projectId: "samvaadai-7f99a",
  storageBucket: "samvaadai-7f99a.firebasestorage.app",
  messagingSenderId: "985704577752",
  appId: "1:985704577752:web:60af74fab732efea9275ad",
  measurementId: "G-F7G793D3XY"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);