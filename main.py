import subprocess
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import gradio as gr
import requests
import json

OLLAMA_SERVER_URL = "http://localhost:11434"  # Replace this with your actual Ollama server URL if different
WHISPER_MODEL_DIR = "./whisper.cpp/models"  # Directory where whisper models are stored


def get_available_models() -> list[str]:
    """
    Retrieves a list of all available models from the Ollama server and extracts the model names.

    Returns:
        A list of model names available on the Ollama server.
    """
    response = requests.get(f"{OLLAMA_SERVER_URL}/api/tags")
    if response.status_code == 200:
        models = response.json()["models"]
        llm_model_names = [model["model"] for model in models]  # Extract model names
        return llm_model_names
    else:
        raise Exception(
            f"Failed to retrieve models from Ollama server: {response.text}"
        )


def get_available_whisper_models() -> list[str]:
    """
    Retrieves a list of available Whisper models based on downloaded .bin files in the whisper.cpp/models directory.
    Filters out test models and only includes official Whisper models (e.g., base, small, medium, large).

    Returns:
        A list of available Whisper model names (e.g., 'base', 'small', 'medium', 'large-V3').
    """
    # List of acceptable official Whisper models
    valid_models = ["base", "small", "medium", "large", "large-V3"]

    # Get the list of model files in the models directory
    model_files = [f for f in os.listdir(WHISPER_MODEL_DIR) if f.endswith(".bin")]

    # Filter out test models and models that aren't in the valid list
    whisper_models = [
        os.path.splitext(f)[0].replace("ggml-", "")
        for f in model_files
        if any(valid_model in f for valid_model in valid_models) and "test" not in f
    ]

    # Remove any potential duplicates
    whisper_models = list(set(whisper_models))

    return whisper_models


def summarize_with_model(llm_model_name: str, context: str, text: str) -> str:
    """
    Uses a specified model on the Ollama server to generate a summary.
    Handles streaming responses by processing each line of the response.

    Args:
        llm_model_name (str): The name of the model to use for summarization.
        context (str): Optional context for the summary, provided by the user.
        text (str): The transcript text to summarize.

    Returns:
        str: The generated summary text from the model.
    """
    prompt = f"""
    You are a professional college administrative officer.

    Your task is to convert the transcript into OFFICIAL MINUTES OF MEETING.

    You MUST follow this exact format:

    GOVERNMENT COLLEGE OF ENGINEERING & TECHNOLOGY, JAMMU

    Minutes of Meeting

    A meeting was held to discuss the agenda items mentioned in the transcript.

    Members Present:
    - If names are mentioned, list them.
    - If names are not mentioned, write: Not clearly mentioned in transcript.

    Proceedings of the Meeting

    1. [Agenda Heading]
    [Write detailed formal discussion paragraph.]

    2. [Agenda Heading]
    [Write detailed formal discussion paragraph.]

    3. [Agenda Heading]
    [Write detailed formal discussion paragraph.]

    Decisions Taken

    1. [Decision Heading]
    [Write formal decision paragraph.]

    2. [Decision Heading]
    [Write formal decision paragraph.]

    3. [Decision Heading]
    [Write formal decision paragraph.]

    The meeting ended with a vote of thanks to the chair.

    STRICT RULES:
    - Do NOT give advice.
    - Do NOT write "Additionally" suggestions.
    - Do NOT write casual summary.
    - Do NOT mention what should be done unless it was discussed.
    - Always use the exact headings above.
    - Output only the final minutes of meeting.

    Context:
    {context if context else "No additional context provided."}

    Transcript:
    {text}
    """

   

    headers = {"Content-Type": "application/json"}
    data = {"model": llm_model_name, "prompt": prompt}

    response = requests.post(
        f"{OLLAMA_SERVER_URL}/api/generate", json=data, headers=headers, stream=True
    )

    if response.status_code == 200:
        full_response = ""
        try:
            # Process the streaming response line by line
            for line in response.iter_lines():
                if line:
                    # Decode each line and parse it as a JSON object
                    decoded_line = line.decode("utf-8")
                    json_line = json.loads(decoded_line)
                    # Extract the "response" part from each JSON object
                    full_response += json_line.get("response", "")
                    # If "done" is True, break the loop
                    if json_line.get("done", False):
                        break
            return full_response
        except json.JSONDecodeError:
            print("Error: Response contains invalid JSON data.")
            return f"Failed to parse the response from the server. Raw response: {response.text}"
    else:
        raise Exception(
            f"Failed to summarize with model {llm_model_name}: {response.text}"
        )


def preprocess_audio_file(audio_file_path: str) -> str:
    """
    Converts the input audio file to a WAV format with 16kHz sample rate and mono channel.

    Args:
        audio_file_path (str): Path to the input audio file.

    Returns:
        str: The path to the preprocessed WAV file.
    """
    output_wav_file = f"{os.path.splitext(audio_file_path)[0]}_converted.wav"

    # Ensure ffmpeg converts to 16kHz sample rate and mono channel
    cmd = f'ffmpeg -y -i "{audio_file_path}" -ar 16000 -ac 1 "{output_wav_file}"'
    subprocess.run(cmd, shell=True, check=True)

    return output_wav_file


def translate_and_summarize(
    audio_file_path: str, context: str, whisper_model_name: str, llm_model_name: str
) -> tuple[str, str]:
    """
    Translates the audio file into text using the whisper.cpp model and generates a summary using Ollama.
    Also provides the transcript file for download.

    Args:
        audio_file_path (str): Path to the input audio file.
        context (str): Optional context to include in the summary.
        whisper_model_name (str): Whisper model to use for audio-to-text conversion.
        llm_model_name (str): Model to use for summarizing the transcript.

    Returns:
        tuple[str, str]: A tuple containing the summary and the path to the transcript file for download.
    """
    output_file = "output.txt"

    print("Processing audio file:", audio_file_path)

    # Convert the input file to WAV format if necessary
    audio_file_wav = preprocess_audio_file(audio_file_path)

    print("Audio preprocessed:", audio_file_wav)

    # Call the whisper.cpp binary
    whisper_command = f'whisper.cpp\\build\\bin\\Release\\whisper-cli.exe -m whisper.cpp\\models\\ggml-{whisper_model_name}.bin -f "{audio_file_wav}" > {output_file}'
    subprocess.run(whisper_command, shell=True, check=True)

    print("Whisper.cpp executed successfully")

    # Read the output from the transcript
    with open(output_file, "r") as f:
        transcript = f.read()

    # Save the transcript to a downloadable file
    transcript_file = "transcript.txt"
    with open(transcript_file, "w") as transcript_f:
        transcript_f.write(transcript)

    # Generate summary from the transcript using Ollama's model
    summary = summarize_with_model(llm_model_name, context, transcript)

    # Clean up temporary files
    os.remove(audio_file_wav)
    os.remove(output_file)

    # Return the downloadable link for the transcript and the summary text
    return summary, transcript_file


# Gradio interface
def gradio_app(
    audio, context: str, whisper_model_name: str, llm_model_name: str
) -> tuple[str, str]:
    """
    Gradio application to handle file upload, model selection, and summary generation.

    Args:
        audio: The uploaded audio file.
        context (str): Optional context provided by the user.
        whisper_model_name (str): The selected Whisper model name.
        llm_model_name (str): The selected language model for summarization.

    Returns:
        tuple[str, str]: A tuple containing the summary text and a downloadable transcript file.
    """
    return translate_and_summarize(audio, context, whisper_model_name, llm_model_name)


# Main function to launch the Gradio interface
if __name__ == "__main__":
    ollama_models = get_available_models()
    whisper_models = get_available_whisper_models()

    custom_css = """
    .gradio-container {
        background: radial-gradient(circle at top, #07162f 0%, #020817 55%, #01030a 100%) !important;
        color: white !important;
        font-family: 'Segoe UI', sans-serif !important;
    }

    #main-title {
        text-align: center;
        font-size: 58px;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #00d4ff, #b56cff, #ff4faf, #ffb347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(0, 212, 255, 0.45);
        margin-bottom: 5px;
    }

    #subtitle {
        text-align: center;
        font-size: 20px;
        color: #d8eaff;
        margin-bottom: 35px;
    }

    .glass-card {
        background: rgba(10, 20, 40, 0.88) !important;
        border: 1px solid rgba(0, 212, 255, 0.35) !important;
        border-radius: 22px !important;
        padding: 22px !important;
        box-shadow: 0 0 35px rgba(0, 212, 255, 0.18) !important;
    }

    .purple-card {
        border: 1px solid rgba(190, 80, 255, 0.45) !important;
        box-shadow: 0 0 35px rgba(190, 80, 255, 0.22) !important;
    }

    #section-heading {
        font-size: 22px;
        font-weight: 800;
        color: #8eeaff;
        margin-bottom: 18px;
    }

    #section-heading-purple {
        font-size: 22px;
        font-weight: 800;
        color: #d8a7ff;
        margin-bottom: 18px;
    }

    #analyze-btn {
        background: linear-gradient(90deg, #ff6a00, #ffb347) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 14px !important;
        height: 55px !important;
        border: none !important;
        box-shadow: 0 0 25px rgba(255, 140, 0, 0.55) !important;
    }

    #reset-btn {
        background: rgba(255,255,255,0.12) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        height: 55px !important;
    }

    textarea, input, select {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    label {
        color: #d8eaff !important;
        font-weight: 700 !important;
    }

    #pipeline {
        background: rgba(8, 15, 35, 0.9);
        border: 1px solid rgba(160, 90, 255, 0.45);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        font-size: 18px;
        color: #ffffff;
        box-shadow: 0 0 25px rgba(160, 90, 255, 0.2);
    }
    """

    with gr.Blocks(
        css=custom_css,
        theme=gr.themes.Soft(),
        title="AI Meeting Summarizer"
    ) as iface:

        gr.Markdown(
            """
            <div id="main-title">🎙️ AI MEETING SUMMARIZER</div>
            <div id="subtitle">Transform your meetings into official minutes with the power of AI</div>
            """
        )

        with gr.Row():
            with gr.Column(scale=1, elem_classes="glass-card"):
                gr.Markdown('<div id="section-heading">① INPUT & SETTINGS</div>')

                audio_input = gr.Audio(
                    type="filepath",
                    label="🎧 Upload Meeting Audio"
                )

                context_input = gr.Textbox(
                    label="📋 Meeting Context",
                    placeholder="Example: Weekly project meeting about deadlines, budget allocation, team updates...",
                    lines=4
                )

                whisper_dropdown = gr.Dropdown(
                    choices=whisper_models,
                    label="🎙️ Whisper Speech Model",
                    value=whisper_models[0]
                )

                ollama_dropdown = gr.Dropdown(
                    choices=ollama_models,
                    label="🧠 AI Summary Model",
                    value=ollama_models[0] if ollama_models else None
                )

                with gr.Row():
                    reset_btn = gr.Button("🔄 Reset Session", elem_id="reset-btn")
                    submit_btn = gr.Button("🚀 Analyze Meeting", elem_id="analyze-btn")

            with gr.Column(scale=1, elem_classes=["glass-card", "purple-card"]):
                gr.Markdown('<div id="section-heading-purple">② MEETING MINUTES GENERATED BY AI</div>')

                summary_output = gr.Textbox(
                    label="📌 AI Generated Meeting Minutes",
                    lines=20,
                    placeholder="Your AI generated meeting minutes will appear here..."
                )

                transcript_file = gr.File(
                    label="⬇️ Download Full Transcript"
                )

        gr.Markdown(
            """
            <div id="pipeline">
            <b>⚡ PROCESSING PIPELINE</b><br><br>
            🎧 Audio → ⚙️ FFmpeg → 🎙️ Whisper.cpp → 📄 Transcript → 🧠 Ollama → 📝 Meeting Minutes
            </div>
            """
        )

        submit_btn.click(
            fn=gradio_app,
            inputs=[
                audio_input,
                context_input,
                whisper_dropdown,
                ollama_dropdown
            ],
            outputs=[
                summary_output,
                transcript_file
            ]
        )

        reset_btn.click(
            fn=lambda: (None, "", "", None),
            inputs=[],
            outputs=[
                audio_input,
                context_input,
                summary_output,
                transcript_file
            ]
        )

    iface.launch(server_name="127.0.0.1", server_port=7861, debug=True)
