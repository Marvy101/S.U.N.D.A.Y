import cv2
import numpy as np
import pyautogui
import os
import time
from PIL import Image
import pytesseract
from pytesseract import Output
from love import openai

chosen_texts = []  # This list will store all the chosen texts

def process_image_and_click_best_choice():
    time.sleep(1)

    # Take screenshot using PyAutoGUI
    screenshot = pyautogui.screenshot()

    # Save the screenshot
    screenshot.save('screenshot.png')

    # Load the image from a file
    image = Image.open('screenshot.png')

    # Use Tesseract to do OCR on the image
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    results = []
    # Print each word and its center coordinates
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 0:  # Only consider items where Tesseract has some confidence
            # Get the bounding box coordinates
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

            # Calculate the center of the bounding box
            center_x = x + w / 2
            center_y = y + h / 2

            # Get the recognized text
            text = data['text'][i]
            # Append the result to the list
            results.append({'Text': text, 'Position': (center_x, center_y)})

    # Use GPT-4 to decide which text to click
    texts = [result["Text"] for result in results]
    print("List of texts to make decision from: ", texts)
    previous_chosen_text = chosen_texts[-1] if chosen_texts else ""  # This will be empty if there are no chosen texts yet
    text_prompt = f"{user_prompt}\nPrevious choice: {previous_chosen_text}\nAll these texts are buttons on a webpage, output the most relevant one to the User Prompt.If you did not find a direct correlatino, select the most related, always select something. Do not output anything else. You cannot type, so try to only click things.\nOptions:\n" + "\n".join(texts)
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a brilliant AI"},
            {"role": "user", "content": text_prompt},
        ],
    )

    chosen_text = response["choices"][0]["message"]["content"]
    chosen_text_info = next((result for result in results if result["Text"] == chosen_text), None)

    if not chosen_text_info:
        print("GPT-4 did not select a valid text. Please try again.")
        return

    print("\n Choice:", chosen_text)
    chosen_texts.append(chosen_text)  # Append the chosen text to the list

    pyautogui.moveTo(chosen_text_info['Position'], duration=0.5)
    pyautogui.doubleClick()


# Example user_prompt
user_prompt = "I want to watch a video about computer"

# Define the GPT-4 interaction to obtain number of iterations
prompt = f'''You are an AI that interacts with a screen. We are starting from the desktop screen. How many times would you need to interact with the screen to accomplish:  user_prompt = {user_prompt}. Output only a number without saying any other thing.'''
response = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=[
        {"role": "system", "content": "You only output numbers"},
        {"role": "user", "content": prompt},
    ],
)

# Extract the number of interactions from the response
num_interactions = int(response["choices"][0]["message"]["content"])

print(num_interactions)

# Call the function with the obtained num_interactions

count = 0
for _ in range(num_interactions):

    if count == 0:
        pyautogui.moveTo(1247, 15, duration=0.5)
        pyautogui.click()

    count = count + 1
    time.sleep(1)

    process_image_and_click_best_choice()
    time.sleep(4)  # sleep a bit to wait for screen changes
