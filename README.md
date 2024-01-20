# SCE VTA App

## Overview

The SCE VTA App is a real-time transit prediction application using the 511 API. It provides up-to-date predictions for the Valley Transportation Authority (VTA) services. This tool is useful for those who frequently use VTA services.

## Getting Started

### Prerequisites

-   Python 3.x
-   Docker
-   Git
-   [511 API Key](https://511.org/open-data/token)

### Installation

1.  **Clone the Repository**  
    Begin by cloning the repository to your local machine:

    ```sh
    git clone https://github.com/ahmadgaz/sce_vta
    ```

2.  **Request 511 API Key**  
    Request a 511 API key from [511.org](https://511.org/open-data/token)

3.  **Configuration**
    Create a `config.yml` file in the root directory of the project. Use `config.example.yml` as a template. Replace the `api_key` value with your 511 API key.

4.  **Set Up a Python Virtual Environment**  
    Initialize a virtual environment in the root directory of the project:

        ```sh
        python -m venv env
        ```

    Activate the virtual environment:

        - Windows Powershell:

        ```sh
         env\Scripts\activate.ps1
        ```

        - MacOS/Linux Bash:

        ```sh
        source sce-venv/bin/activate
        ```

5.  **Run the Application**  
    Run the application using docker-compose:

        - Docker:

        ```sh
        docker-compose up --build
        ```

    Alternatively, run the application without caching or prometheus using python:

        - Python:

        ```sh
        python api/app.py
        ```

6.  **View the Application**  
    The application will be running on `localhost/predictions` by default.
