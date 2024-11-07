import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from "react-router-dom";
import axios from 'axios';
import '../App.css';
import { Link } from 'react-router-dom';
import { useNavigate } from "react-router-dom";
import "../css/classesAdmissions.css";
import AdminNavbar from './AdminNavbar';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function AddTimetable() {
    const [userDetails, setuserDetails] = useState(null);

    const location = useLocation();
    useEffect(() => {
        setuserDetails(location.state?.userDetails);
    }, []);
    console.log("I am here")
    console.log("userdetails in admin", userDetails);

    const navigate = useNavigate();

    const handleViewTimetable = () => {
        navigate('/timetable');
        window.location.reload();
    };

    const [formData, setFormData] = useState({
        semester: '',
        department: '',
        day: '',
        slot_1: '',
        slot_2: '',
        slot_3: '',
        slot_4: '',
        slot_5: '',
        slot_6: '',
        slot_7: '',
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('Form Data:', formData);
        try {
            //admin functionality
            const response = await axios.post('http://127.0.0.1:8000/api/addTimetable/', formData);
            console.log('Response:', response);
            if (response.status === 201) {
                toast.success("Data Added Successfully");
                console.log('Data added successfully');
                // setFormData({
                //     semester: '',
                //     department: '',
                //     day: '',
                //     slot_1: '',
                //     slot_2: '',
                //     slot_3: '',
                //     slot_4: '',
                //     slot_5: '',
                //     slot_6: '',
                //     slot_7: '',
                // });
            }
        }
        catch (error) {
            console.error('Error adding timetable data:', error);
            if (error.response && error.response.data) {
                toast.error("Data already exists");
                console.log('Validation Errors:', error.response.data);
            }
        }
        setFormData({
            semester: '',
            department: '',
            day: '',
            slot_1: '',
            slot_2: '',
            slot_3: '',
            slot_4: '',
            slot_5: '',
            slot_6: '',
            slot_7: '',
        });
    };

    return (
        <>
            <AdminNavbar user_details={userDetails} />
            <div className='add-timetable'>
                <div className="header">
                    <p>Add Timetable</p>
                </div>
                <div>
                    <div className='inputs'>
                        <form onSubmit={handleSubmit}>
                            <label><p>Semester</p>:<span>
                                <input type="text" id="semester" name="semester" value={formData.semester} onChange={handleChange} required /></span></label>

                            <label><p>Department</p>:<span>
                                <input type="text" id="department" name="department" value={formData.department} onChange={handleChange} required /></span></label>

                            <label><p>Day</p>:<span>
                                <input type="text" id="day" name="day" value={formData.day} onChange={handleChange} required /></span></label>

                            <label><p>Slot 1</p>:<span>
                                <input type="text" id="slot_1" name="slot_1" value={formData.slot_1} onChange={handleChange} /></span></label>

                            <label><p>Slot 2</p>:<span>
                                <input type="text" id="slot_2" name="slot_2" value={formData.slot_2} onChange={handleChange} /></span></label>

                            <label><p>Slot 3</p>:<span>
                                <input type="text" id="slot_3" name="slot_3" value={formData.slot_3} onChange={handleChange} /></span></label>

                            <label><p>Slot 4</p>:<span>
                                <input type="text" id="slot_4" name="slot_4" value={formData.slot_4} onChange={handleChange} /></span></label>

                            <label><p>Slot 5</p>:<span>
                                <input type="text" id="slot_5" name="slot_5" value={formData.slot_5} onChange={handleChange} /></span></label>

                            <label><p>Slot 6</p>:<span>
                                <input type="text" id="slot_6" name="slot_6" value={formData.slot_6} onChange={handleChange} /></span></label>

                            <label><p>Slot 7</p>:<span>
                                <input type="text" id="slot_7" name="slot_7" value={formData.slot_7} onChange={handleChange} /></span></label>

                            <button type="submit">Add Timetable</button>
                        </form>
                    </div>
                    <ToastContainer />
                </div>
                <br />
                <br />

            </div>
        </>
    );
}

export default AddTimetable;




