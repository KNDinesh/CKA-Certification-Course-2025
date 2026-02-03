from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Docker!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Flask is a light weight web framework for python that is widely used for building web applications and APIs. Code above is for a basic python flask application that says "Hello, Docker!". It listens on Port 5000.
# We will containerize this application using Docker. Now to continue, go back to the Dockerfile to understand the steps and for more details related to Dockerfile refer README.md.
