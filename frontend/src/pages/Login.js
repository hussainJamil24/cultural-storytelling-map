import Navbar from '../components/Navbar';
import { useState } from 'react';
import '../assets/styles/login.css';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSignIn = (e) => {
    e.preventDefault();
    // console.log('Sign in with:', { email, password });
    };

    return (
        <div className="login-page d-flex flex-column">
            {/* Navbar */}
            <Navbar/>
            <div className="login-container d-flex">
                {/* left side */}
                <div className="login-left d-flex align-items-center justify-content-end">
                        <div className="branding-content">
                            <div className="accent-line mb-5"></div>
                            <h2>Every story finds its place.</h2>
                            <p className='fw-lighter'>Securely access your curated collection of oral histories and heritage landmarks.</p>

                            <div className="profile-avatars d-flex align-items-center gap-2">
                                <div className="avatar avatar-1"></div>
                                <div className="avatar avatar-2"></div>
                                <button className="avatar-add d-flex align-items-center justify-content-center">+</button>
                            </div>
                        </div>
                </div>

                {/* right side */} 
                <div className="login-right d-flex align-items-center justify-content-start">
                        <div className="login-card">
                            <h1 className='text-center mb-3 fw-semibold'>Welcome Back</h1>
                            <p className="login-subtitle text-center mb-5 fw-lighter">Enter your credentials to access your heritage collection.</p>
                            
                            {/* list form */}
                            <form onSubmit={handleSignIn}
                            className='d-flex flex-column gap-3'>
                                {/* email field */}
                                <div className="form-group d-flex flex-column gap-1">
                                    <label htmlFor="email">EMAIL ADDRESS</label>
                                    <div className="input-wrapper">
                                        <input type="email" placeholder="curator@ethereal.map"
                                            id="email" value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* email field */}
                                <div className="form-group d-flex flex-column gap-1">
                                    <div className="password-label d-flex align-items-center justify-content-between">
                                        <label htmlFor="password">PASSWORD</label>
                                        <a href="#forgot" className="forgot-link">Forgot?</a>
                                    </div>
                                    <div className="input-wrapper d-flex align-items-center">
                                        <input type="password" placeholder="••••••••"
                                            id="password" value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* sign in button */}
                                <button type="submit" className="signin-button mt-3">
                                    SIGN IN
                                </button>
                            </form>

                            {/* register link */}
                            <div className="register-section fw-light text-center mt-4 pt-3">
                                <span>New to the archive? </span>
                                <a href="#register" className="register-link fw-semibold">Register</a>
                            </div>
                        </div>
                </div>
            </div>
        </div>
    );
}