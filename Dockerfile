# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=giveaway_flask.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the app. "flask run" is the recommended way to start a development server.
CMD ["flask", "run"]```

### Step 5: How to Run Your New Application

Your `main.py` is now obsolete. The workflow is entirely managed by Flask and Docker.

1.  **Build the Docker Image:**
    Open a terminal in your project's root folder (`giveAway/`) and run:
    ```bash
    docker build -t giveaway-app .
    ```

2.  **Run the Docker Container (This is the most important command):**
    Now, run the image you just built. The `-v` flag is the key to session persistence.
    ```bash
    docker run -p 5000:5000 -v "$(pwd)/sessions:/app/sessions" --name giveaway-container giveaway-app
    ```
    *   `-p 5000:5000`: Maps your computer's port 5000 to the container's port 5000.
    *   `-v "$(pwd)/sessions:/app/sessions"`: This is the Docker Volume. It maps the `sessions` folder you created on your computer to the `/app/sessions` folder inside the container. **Any file saved to `/app/sessions` will actually be saved on your computer, surviving container restarts.**
    *   `--name giveaway-container`: Gives your running container a memorable name.

3.  **Use the App:**
    *   Open your web browser and go to `http://127.0.0.1:5000`.
    *   You will see the new login page. Enter your credentials and the post shortcode.
    *   If 2FA is needed, the page will reload and ask for the code.
    *   Once scraping is complete, you'll be redirected to the settings page.
    *   From there, everything works as it did before!

4.  **To Stop and Start the Container:**
    *   To stop: `docker stop giveaway-container`
    *   To start again later: `docker start giveaway-container`
    *   To view logs: `docker logs -f giveaway-container`