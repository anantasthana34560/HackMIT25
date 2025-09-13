import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/plan", methods=["POST"])
def plan():
    destination = request.form.get("destination")
    dates = request.form.get("dates")
    style = request.form.get("style")

    prompt = f"""
    You are a travel planner. Create a short 3-day itinerary for a trip.
    Destination: {destination}
    Dates: {dates}
    Style: {style}
    Return the plan as a list of day-by-day suggestions with activities and meals.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # faster + cheaper model, you can also use gpt-4 or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are an expert travel planner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        plan_text = response.choices[0].message.content
    except Exception as e:
        plan_text = f"Error: {e}"

    return f"""
    <h1>Your AI Trip Plan</h1>
    <pre>{plan_text}</pre>
    <a href="/">Go Back</a>
    """

if __name__ == "__main__":
    app.run(debug=True)
