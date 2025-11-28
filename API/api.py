from fastapi import FastAPI

app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to my FastAPI app!"}

@app.get("/welcome")
def welcome():
    return {"message": "Welcome to my FastAPI app!"}

# Example GET API with a parameter
@app.get("/user")
def user_profile():
    return {
        "name": "RangeshPandian PT",
        "Channel": "Info With Rangesh",
        "Website": "https://rangesh-portfolio.netlify.app/",
        "LinkedIn": "https://www.linkedin.com/in/rangeshpandian-pt-428b04325/"
    }

@app.get("/user/{user_id}")
def user_profile(user_id: int):
    if user_id == 1:
        return {
            "name": "RangeshPandian PT",
            "Channel": "Info With Rangesh",
            "Website": "https://rangesh-portfolio.netlify.app/",
            "LinkedIn": "https://www.linkedin.com/in/rangeshpandian-pt-428b04325/"
        }
    else:
        return {
            "name": "John" + str(user_id),
            "Channel": "Info with Rangesh",
            "Website": "https://rangesh-portfolio.netlify.app/",
            "LinkedIn": "https://www.linkedin.com/in/rangeshpandian-pt-428b04325/"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

