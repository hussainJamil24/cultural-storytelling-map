import '../assets/styles/sidebar.css'

export default function Sidebar() {
    return (
        <div className="sidebar d-flex flex-column bg-light p-4" style={{widows:"350px"}}>
            <h5>Categories</h5>
            <p className="text-muted small">Filter stories</p>

            <ul className="sidebar-menu d-flex flex-column">
                <li className='active'>
                    <a className="menu-link  d-flex align-items-center"> 
                        <i class="bi bi-grid-fill"></i>
                        <span>All</span>
                    </a>
                </li>

                <li>
                    <a className="menu-link d-flex align-items-center">
                        <i class="bi bi-journal-bookmark"></i>
                        <span>Heritage</span>
                    </a>
                </li>

                <li>
                    <a className="menu-link  d-flex align-items-center">
                        <i class="bi bi-bank2"></i>
                        <span>Landmarks</span>
                    </a>
                </li>

                <li>
                    <a className="menu-link  d-flex align-items-center">
                        <i class="bi bi-mic-fill"></i>
                        <span>Oral Histories</span>
                    </a>
                </li>

                <li>
                    <a className="menu-link  d-flex align-items-center">
                        <i class="bi bi-stars"></i>
                        <span>Customs</span> 
                    </a>
                </li>
            </ul>

            <button className="upload-btn">
                <i className="bi bi-plus-lg"></i>
                Upload Story
            </button>
        </div>
    );
}