import Navbar from '../components/Navbar';
import { useState, useEffect } from 'react';
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import '../assets/styles/login.css';
import API from "../services/Api";


// renders the login page layout and form shell
export default function Login() {

    const [stories, setStories] = useState([]);

    useEffect(() => {
        const fetchStories = async () => {
            try {
                const res = await API.get("/stories");
                setStories(res.data.filter(s => s.image_url).slice(0, 2)); // only 2 images
            } catch (err) {
                console.error(err);
            }
        };

        fetchStories();
    }, []);

    // navigation (redirect after login)
    const navigate = useNavigate();

    // error
    const [error, setError] = useState("");

    // stores the local login form values
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    // prevents page refresh until authentication is implemented
    const handleSignIn = async (e) => {
    e.preventDefault();
    setError("");

    try{
        const form = new FormData();
        form.append("email", email);
        form.append("password", password);

        const res = await API.post("/login", form, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
            
        });

        // console.log(res.data);

        if (res.data.error || res.data.detail) {
            setError(res.data.error || res.data.detail);
            return;
        }

        // Clear inputs after success
        setEmail("");
        setPassword("");

        // alert("Login successful!");
        
        // save data on localstorage & redirict to map page
        localStorage.setItem("access_token", res.data.access_token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        localStorage.setItem("isAdmin", res.data.is_admin);

        // redirect after login
        if (res.data.is_admin === true) {
            navigate("/admin");
        } else {
            navigate("/");
        }

    } catch (err) {
        console.error(err);
        // alert("Login failed");
        const message = err.response?.data?.detail || "Invalid email or password";

        setError(message);
    }

    // console.log('Sign in with:', { email, password });
    };

    useEffect(() => {
        const user = localStorage.getItem("user");
        const isAdmin = localStorage.getItem("isAdmin");


        // BLOCK access without login
        if (user) {
            if (isAdmin === "true") {
                navigate("/admin");
            } else {
                navigate("/");
            }
        }
    }, [navigate]);

    const disabled = !email || !password;

    return (
        <div className="login-page d-flex flex-column">
            {/* shows the shared site navigation */}
            <Navbar/>
            <div className="login-container d-flex">
                {/* shows the brand message panel */}
                <div className="login-left d-flex align-items-center justify-content-center">
                        <div className="branding-content">
                            <div className="accent-line mb-5"></div>
                            <h2>Every story finds its place.</h2>
                            <p className='fw-lighter'>Securely access your curated collection of oral histories and heritage landmarks.</p>

                            <div className="profile-avatars d-flex align-items-center gap-2">
                                {stories.map((story) => {
                                    const isImage = story.media_url?.match(/\.(jpg|jpeg|png|webp|gif)$/i);

                                    return (
                                    <img
                                        key={story.id}
                                        src={
                                        isImage
                                            ? `http://127.0.0.1:8000/${story.media_url}`
                                            : "https://via.placeholder.com/40"
                                        }
                                        alt={story.title}
                                        className="avatar-img"
                                    />
                                    );
                                })}
                                <button className="avatar-add d-flex align-items-center justify-content-center">+</button>
                            </div>
                        </div>
                </div>

                {/* shows the sign-in form card */}
                <div className="login-right d-flex align-items-center justify-content-center">
                        <div className="login-card">
                            <h1 className='text-center mb-3 fw-semibold'>Welcome Back</h1>
                            <p className="login-subtitle text-center mb-5 fw-lighter">Enter your credentials to access your heritage collection.</p>
                            
                            {/* show error */}
                            {error && <p className="text-danger">{error}</p>}

                            {/* collects email and password inputs */}
                            <form onSubmit={handleSignIn}
                            className='d-flex flex-column gap-3'>
                                {/* collects the email address */}
                                <div className="form-group d-flex flex-column gap-1">
                                    <label htmlFor="email">EMAIL ADDRESS</label>
                                    <div className="input-wrapper d-flex align-items-center">
                                        <i className="bi bi-envelope input-icon"></i>
                                        <input type="email" placeholder="example@gmail.com"
                                            id="email" value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* collects the password */}
                                <div className="form-group d-flex flex-column gap-1">
                                    <div className="password-label d-flex align-items-center justify-content-between">
                                        <label htmlFor="password">PASSWORD</label>
                                        <a href="#forgot" className="forgot-link">Forgot?</a>
                                    </div>
                                    <div className="input-wrapper d-flex align-items-center">
                                        <i className="bi bi-lock input-icon"></i>
                                        <input type="password" placeholder="••••••••"
                                            id="password" value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* submits the login form */}
                                <button type="submit" className="signin-button mt-3" disabled={disabled}>
                                    SIGN IN
                                </button>
                            </form>

                            {/* shows the register prompt */}
                            <div className="register-section fw-light text-center mt-4 pt-3">
                                <span>New to the archive? </span>
                                <Link to="/register" className="register-link fw-semibold">Register</Link>
                            </div>
                        </div>
                </div>
            </div>
        </div>
    );
}
