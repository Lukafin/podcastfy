from flask import Flask, request, send_file
#from podcastfy.client import generate_podcast
from client import generate_podcast
import os
import logging

app = Flask(__name__)

# Configure logging
#logging.basicConfig(level=logging.DEBUG)

@app.route('/generate_podcast', methods=['GET'])
def get_podcast():
    urls = request.args.getlist('url')
    
    if not urls:
        app.logger.debug("No URLs provided in request")
        return "Error: No URLs provided", 400

    try:
        # Generate the podcast and get the file path
        audio_file_path = generate_podcast(urls=urls)
        app.logger.debug(f"Generated podcast file at: {audio_file_path}")
        
        # Verify that the file exists
        if not os.path.isfile(audio_file_path):
            app.logger.error(f"Generated file does not exist: {audio_file_path}")
            return "Error: Generated audio file does not exist", 500

        # Send the file directly
        response = send_file(
            audio_file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='podcast.mp3'
        )
        app.logger.debug("Sending file to client")

        # Schedule the temporary file for deletion after sending
        @response.call_on_close
        def delete_temp_file():
            try:
                os.remove(audio_file_path)
                app.logger.debug(f"Deleted temporary file: {audio_file_path}")
            except Exception as e:
                app.logger.error(f"Failed to delete temporary file {audio_file_path}: {e}")

        return response

    except Exception as e:
        app.logger.exception("An error occurred while generating the podcast")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
