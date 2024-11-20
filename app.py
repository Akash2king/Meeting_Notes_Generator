from flask import Flask, request, jsonify, render_template
import assemblyai as aai
from groq import Groq
import markdown
import os
from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()
app = Flask(__name__)
# Set AssemblyAI API key
aai.settings.api_key = os.getenv('AAI_API_KEY')
# Set Groq API key
groq_client = Groq(api_key=os.getenv('GORQ_API_KEY'))
def transcribe_audio(audio_file):
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file,config=config)
    if transcript.status == aai.TranscriptStatus.error:
        return None, f"Transcription failed: {transcript.error}"
    return transcript.text, None
def generate_notes(text):
    text=f"""{text}"""
    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": """You are an expert assistant. Your task is to process the following transcription and generate two sections in 5000 words: 

    1. Summary: A concise paragraph summarizing the main ideas and overall content of the transcription. Focus on the essence of the discussion without losing important context.

    2. Key Points: A structured list of the most important points covered in the transcription, highlighting key information, important insights, and any critical data or conclusions. Each point should be brief but informative.

    Transcription: \"{transcript_text}\"\n\nPlease provide the summary and key points below:\n- Summary:\n  \n- Key Points:\n  1. \n  2. \n  3. \n  ...\n provide in plain text in 5000 words"""
            },
            {
                "role": "user",
                "content": f"""{text}"""
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    new=''
    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")
        new += chunk.choices[0].delta.content or ""
    return new


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_file = request.files.get('audio_file')  # Get the uploaded file
    if not audio_file:
        return jsonify({'error': 'Audio file is required'}), 400
    
    uploads_dir = "./uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

# Save the file temporarily
    audio_file_path = os.path.join(uploads_dir, audio_file.filename)
    audio_file.save(audio_file_path)

    # Transcribe the audio
    transcript_text, error = transcribe_audio(audio_file_path)
    print(transcript_text)
    if error:
        return jsonify({'error': error}), 500
    
    # Generate notes from the transcription
    notes = generate_notes(transcript_text)
    print(notes)

    # Clean up the uploaded file after processing
    os.remove(audio_file_path)

    return render_template('result.html', transcript=transcript_text, notes=notes)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
