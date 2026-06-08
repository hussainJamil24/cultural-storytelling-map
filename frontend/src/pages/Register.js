import { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../assets/styles/login.css";
import API from "../services/Api";

export default function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        confirmPassword: ""
    });

    const handleChange = (e) => {
        const {name, value} = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.password !== formData.confirmPassword) {
            alert("Passwords do not match");
            return;
        }

        try {
            const form = new FormData();
            form.append("name", formData.name);
            form.append("email", formData.email);
            form.append("password", formData.password);

            const res = await API.post("/register", form, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            if (res.data.error) {
                alert(res.data.error);
                return;
            }

            console.log(res.data);
            alert("Registered successfully!");

            navigate("/login")

        } catch (err) {
            console.error(err);
        alert("Registration failed");
        }

        // console.log("Register data:", formData);
    };

    const disabled =
    !formData.name ||
    !formData.email ||
    !formData.password ||
    !formData.confirmPassword;

    return(
        <div style={{background:"#f0f2f5"}}>
            {/* navbar */}
            <Navbar/>

            {/* container */}
            <div className="container d-flex justify-content-center align-items-center vh-100">
                <div className="card p-4 shadow" style={{ width: "400px" }}>
                    <h3 className="text-center mb-4">Create Account</h3>

                    {/* form registration */}
                    <form onSubmit={handleSubmit}>
                        {/* name */}
                        <div className="mb-3">
                            <input type="text" name="name" className="form-control" placeholder="Full Name"
                            value={formData.name} onChange={handleChange} required/>
                        </div>

                        {/* email */}
                        <div className="mb-3">
                            <input type="email" name="email" className="form-control" placeholder="Email"
                            value={formData.email} onChange={handleChange} required/>
                        </div>

                        {/* password */}
                        <div className="mb-3">
                            <input type="password" name="password" className="form-control" placeholder="Password"
                            value={formData.password} onChange={handleChange} required/>
                        </div>

                        {/* confirm password */}
                        <div className="mb-3">
                            <input type="password" name="confirmPassword" className="form-control" placeholder="Confirm Password"
                            value={formData.confirmPassword} onChange={handleChange} required/>
                        </div>

                        {/* submit */}
                        <button type="submit" disabled={disabled} className="reg-button w-100">Register</button>
                    </form>

                    {/* link to login */}
                    <p className="text-center mt-3">
                        Already have an account?{" "}
                        <Link to="/login">Login</Link>
                    </p>
                </div>
            </div>
        </div>
    )
}