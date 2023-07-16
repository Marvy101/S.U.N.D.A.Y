import cv2
import numpy as np
import pyautogui
import os
import time
from PIL import Image
import pytesseract
from pytesseract import Output
import openai

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

            # Print the result
            print(f'Text: {text}, Position: ({center_x}, {center_y})')

    # Use GPT-4 to decide which text to click
    texts = [result["Text"] for result in results]
    print("List of texts to make decision from: ", texts)
    text_prompt = f"{user_prompt}\n All these texts are buttons on a webpage, output the most relevant one to the User Prompt. Do not output anything else/ \n \nOptions:\n" + "\n".join(texts)
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a brilliant comedian"},
            {"role": "user", "content": text_prompt},
        ],
    )

    chosen_text = response["choices"][0]["message"]["content"]
    chosen_text_info = next((result for result in results if result["Text"] == chosen_text), None)

    if not chosen_text_info:
        print("GPT-4 did not select a valid text. Please try again.")
        return

    print("\n Choice:", chosen_text)

    pyautogui.moveTo(chosen_text_info['Position'], duration=0.5)
    pyautogui.click(x=chosen_text_info['Position'][0], y=chosen_text_info['Position'][1])


# Example user_prompt
user_prompt = "Click Youtube Icon"

# Define the GPT-4 interaction to obtain number of iterations
prompt = f'''You are an AI that interacts with a screen. How many times should you interact to accomplish: user_prompt = {user_prompt}. Output only a number without saying any other thing.'''
response = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=[
        {"role": "system", "content": "You are only output numbers"},
        {"role": "user", "content": prompt},
    ],
)

# Extract the number of interactions from the response
num_interactions = int(response["choices"][0]["message"]["content"])

print(num_interactions)

# Call the function with the obtained num_interactions
for _ in range(num_interactions):
    process_image_and_click_best_choice()
    time.sleep(2)  # sleep a bit to wait for screen changes
