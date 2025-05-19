import google.generativeai as genai


# Set your API key here (better to use environment variables in production)

genai.configure(api_key="AIzaSyA_LfnvKFq5dLFKYpArkIXwjxqgiZaFD1s")
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)
def enhance_prompt(raw_prompt: str) -> str:
    response = model.generate_content([
        "\"You are a creative poster designer.Given a short prompt, you must turn it into a highly descriptive visual prompt suitable for generating posters.Focus on tone, emotion, and rich details. Keep it under 50 words.",
      f"input:{raw_prompt} ",
      "output: ",
    ])
    return response.text

