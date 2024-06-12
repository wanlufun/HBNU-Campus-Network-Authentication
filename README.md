# HBNU Campus Network Authentication

A scirpt that can authenticate to the HBNU campus network via CLI.

> [!WARNING]
> This script is specifically designed for use at HBNU University. If you are not a member of this institution, the script may not be applicable or useful to you.


## Configuration
1. Create Environment File:
   * In the same directory as auth.exe, create a .env file to store your environment variables.
2. Edit the .env File:
   * Use a text editor to fill in your environment variables. Below is the template you should follow:
   ```text
   # Student Account
   USERNAME_STUDENT_ID=your_student_id_here
   PASSWORD_STUDENT_ID=your_password_here

   # Campus Network Account
   USERNAME_PHONE=your_phone_number_here
   PASSWORD_PHONE=your_password_here
   ```
   Replace your_student_id_here, your_password_here, and your_phone_number_here with your actual credentials.


## Usage
1. "Download the latest GitHub release that matches your system's architecture.

2. [Configuration](#configuration)

3. Double-click the .exe file to execute it.


## Explanation of Environment Variables

| Variable                | Description                                    | Context                                                                                                 |
|-------------------------|------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| `USERNAME_STUDENT_ID`   | Your HBNU student ID.                          | Commonly used in school computer labs and labs.                                                         |
| `PASSWORD_STUDENT_ID`   | Password associated with your student ID.      | --                                                                                                      |
| `USERNAME_PHONE`        | Phone number registered with the campus network. | Used by students who have subscribed to campus network packages from the three major telecom operators. |
| `PASSWORD_PHONE`        | Password for the phone number account.         | --                                                                                                      |


## Acknowledgments

This project utilizes the following open-source Python libraries:

* python-dotenv: A library for managing environment variables from .env files, making it easier to configure applications in development and production environments.

* requests: An elegant and simple HTTP library for Python, built for human beings.

We extend our sincere thanks to the developers and contributors of these libraries for their valuable work, which has significantly contributed to the development of this project.


## License
MIT License. See [License here](./LICENSE) for details.

