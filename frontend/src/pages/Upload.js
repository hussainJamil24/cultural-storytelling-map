// import { useState } from "react";
import Navbar from '../components/Navbar';
import '../assets/styles/uploadstory.css';
export default function Upload() {
    return (
        <div className="upload-story-container bg-light">
            {/* Navbar */}
            <Navbar/>

            {/* Header */}
            <div className="story-header text-center mt-5">
                <h1 className='fw-bolder mb-3'>Share a Fragment of History</h1>
                <p className='fw-lighter m-0'>Pin your story to the living map of our collective heritage.</p>
            </div>

            {/* Main Form */}
            <div className="story-card">
                <form>
                    {/* Story Title */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium '>Story Title</label>
                        <input type='text' name='title' className='form-control p-3'
                        placeholder='Enter a memorable name for your story'
                        />
                    </div>

                    {/* The Narrative */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium'>The narrative</label>
                        <textarea type='text' name='narrative' className='form-control textarea-large p-3' rows="6"
                        placeholder='Describe the memory, the event, or the significance of this place....'
                        >
                        </textarea>
                    </div>

                    {/* Upload Boxes */}
                    <div className="upload-boxes">
                        {/* Upload Images */}
                        <div className="upload-box text-center">
                            <input type="file" id="images-input" multiple accept="image/*"
                            // style={{ display: 'none' }}    
                            />
                            <label htmlFor="images-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-image"></i>
                                </div>
                                <h6>Upload Images</h6>
                                <p className='fw-lighter'>PNG, JPG up to 10MB</p>
                            </label>
                        </div>

                        {/* Add Oral History */}
                        <div className="upload-box text-center">
                            <input type="file" id="audio-input" accept="audio/*"
                            // style={{ display: 'none' }}    
                            />
                            <label htmlFor="audio-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-mic"></i>
                                </div>
                                <h6>Add Oral History</h6>
                                <p className='fw-lighter'>MP3, WAV up to 20MB</p>
                            </label>
                        </div>

                    </div>

                </form>
            </div>
        </div>
    );
}