import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def list_available_models():
    """Lists the available generative models."""
    try:
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                print(f"Model Name: {model.name}")
                print(f"Description: {model.description}")
                
                # Safely check for input and output modalities
                input_modality = getattr(model, 'input_modality', 'Not Available')
                output_modality = getattr(model, 'output_modality', 'Not Available')
                
                print(f"Input Modalities: {input_modality}")
                print(f"Output Modalities: {output_modality}")
                
                # Print generation methods if available
                print(f"Generation Methods: {model.supported_generation_methods}")
                print("-" * 30)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_available_models()
