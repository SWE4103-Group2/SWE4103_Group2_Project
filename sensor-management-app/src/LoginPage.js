import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './App';


// Create a functional component for the login page
const LoginPage = () => {
  const [selectedAccount, setSelectedAccount] = useState('researcher');
  // State to store user input (username and password)
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleAccountChange = (event) => {
    setSelectedAccount(event.target.value);
  };

  // Function to handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Simulating authentication logic (replace with your actual authentication logic)
    if (username !== '' && password !== '') {
      // Call a function to update the authentication state (setAuthenticated(true))
      login(selectedAccount);
      
      // Redirect to the intended route (e.g., '/')
      navigate('/');
    } else {
      // Handle authentication failure (e.g., show an error message)
      console.log('Authentication failed');
    }

    // Reset the form after submission
    setUsername('');
    setPassword('');
  };

  return (
    <html>
      <head>
        <title>Sensory Management System</title>
        <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet"/>
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.4.1/css/all.css" integrity="sha384-5sAR7xN1Nv6T6+dT2mhtzEpVJvfS3NScPQTrOxhwjIuvcA67KV2R5Jz6kr4abQsz" crossOrigin="anonymous"/>
        <style>
          {`
            html, body {
            display: flex;
            justify-content: center;
            height: 100%;
            }
            body, div, h1, form, input, p { 
            padding: 0;
            margin: 0;
            outline: none;
            font-family: Roboto, Arial, sans-serif;
            font-size: 16px;
            color: #666;
            }
            h1 {
            padding: 10px 0;
            font-size: 32px;
            font-weight: 300;
            text-align: center;
            }
            p {
            font-size: 12px;
            }
            hr {
            color: #a9a9a9;
            opacity: 0.3;
            }
            .main-block {
            max-width: 340px; 
            min-height: 460px; 
            padding: 10px 0;
            margin: auto;
            border-radius: 5px; 
            border: solid 1px #ccc;
            box-shadow: 1px 2px 5px rgba(0,0,0,.31); 
            background: #ebebeb; 
            }
            form {
            margin: 0 30px;
            }
            .account-type, .gender {
            margin: 15px 0;
            }
            input[type=radio] {
            display: none;
            }
            label#icon {
            margin: 0;
            border-radius: 5px 0 0 5px;
            }
            label.radio {
            position: relative;
            display: inline-block;
            padding-top: 4px;
            margin-right: 20px;
            text-indent: 30px;
            overflow: visible;
            cursor: pointer;
            }
            label.radio:before {
            content: "";
            position: absolute;
            top: 2px;
            left: 0;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #1c87c9;
            }
            label.radio:after {
            content: "";
            position: absolute;
            width: 9px;
            height: 4px;
            top: 8px;
            left: 4px;
            border: 3px solid #fff;
            border-top: none;
            border-right: none;
            transform: rotate(-45deg);
            opacity: 0;
            }
            input[type=radio]:checked + label:after {
            opacity: 1;
            }
            input[type=text], input[type=password] {
            width: calc(100% - 57px);
            height: 36px;
            margin: 13px 0 0 -5px;
            padding-left: 10px; 
            border-radius: 0 5px 5px 0;
            border: solid 1px #cbc9c9; 
            box-shadow: 1px 2px 5px rgba(0,0,0,.09); 
            background: #fff; 
            }
            input[type=password] {
            margin-bottom: 15px;
            }
            #icon {
            display: inline-block;
            padding: 9.3px 15px;
            box-shadow: 1px 2px 5px rgba(0,0,0,.09); 
            background: #1c87c9;
            color: #fff;
            text-align: center;
            }
            .btn-block {
            margin-top: 10px;
            text-align: center;
            }
            button {
            width: 100%;
            padding: 10px 0;
            margin: 10px auto;
            border-radius: 5px; 
            border: none;
            background: #1c87c9; 
            font-size: 14px;
            font-weight: 600;
            color: #fff;
            }
            button:hover {
            background: #26a9e0;
            }
          `}
        </style>
      </head>
      <body>
        <div className="main-block">
          <h1>Registration</h1>
          <form action="/">
            <hr />
            <div className="account-type">
              <input type="radio" value="researcher" id="radioOne" name="account"
                checked={selectedAccount === 'researcher'}
                onChange={handleAccountChange}
              />
              <label htmlFor="radioOne" className="radio">Researcher</label>
              <input type="radio" value="scientist" id="radioTwo" name="account"
                checked={selectedAccount === 'scientist'}
                onChange={handleAccountChange}
              />
              <label htmlFor="radioTwo" className="radio">Scientist</label>
              <input type="radio" value="technician" id="radioThree" name="account"
                checked={selectedAccount === 'technician'}
                onChange={handleAccountChange}
              />
              <label htmlFor="radioThree" className="radio">Technician</label>
            </div>
            <hr />
            <label id="icon" htmlFor="name"><i className="fas fa-envelope"></i></label>
            <input type="text" name="name" id="username" placeholder="Username" value={username} required
              onChange={(e) => setUsername(e.target.value)}
            />
            <label id="icon" htmlFor="name"><i className="fas fa-unlock-alt"></i></label>
            <input type="password" name="name" id="password" placeholder="Password" value={password} required
              onChange={(e) => setPassword(e.target.value)}
            />
            <hr />
            <div className="btn-block">
              <p>By clicking Register, you agree on our <a href="https://www.unb.ca/">Privacy Policy</a>.</p>
              <button onClick={handleSubmit}>Login</button>
            </div>
          </form>
        </div>
      </body>
    </html>
  );
};

// Export the component for use in other parts of the application
export default LoginPage;