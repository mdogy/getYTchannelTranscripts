import os
import sys
import argparse
import logging
import pandas as pd
import yaml
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcripts.core.utils import generate_unique_filename

# --- Basic Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
load_dotenv()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Summarize video transcripts using Google's Gemini API."
    )
    parser.add_argument("--csv-path", required=True, help="Path to the input CSV file.")
    parser.add_argument(
        "--transcripts-dir", required=True, help="Directory containing raw transcript files."
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory to save summary files."
    )
    parser.add_argument(
        "--prompt-path", required=True, help="Path to the prompt template file."
    )
    parser.add_argument(
        "--config-path", required=True, help="Path to the YAML configuration file."
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of videos to process."
    )
    return parser.parse_args()


def initialize_model(config_path):
    """Initialize the Google Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    model_name = config.get("model", "gemini-1.5-pro-latest")
    generation_config = config.get("generation_config", {})
    return genai.GenerativeModel(model_name, generation_config=generation_config)


def process_video(row, model, prompt_template, args):
    """Process a single video."""
    video_id = row.get("video_id")
    video_title = row.get("title", "No Title")
    video_description = row.get("description", "No Description")
    csv_row_data = row.to_json(indent=2)

    if not video_id:
        logging.warning("Skipping row due to missing video_id.")
        return

    summary_path = os.path.join(args.output_dir, f"{video_id}_summary.txt")
    if os.path.exists(summary_path):
        logging.info(f"Summary for {video_id} already exists. Skipping.")
        return

    transcript_filename = generate_unique_filename(video_title, video_id)
    transcript_path = os.path.join(args.transcripts_dir, transcript_filename)
    if not os.path.exists(transcript_path):
        logging.error(
            f"Transcript for {video_id} not found at {transcript_path}. Skipping."
        )
        return

    try:
        with open(transcript_path, "r") as f:
            transcript_text = f.read()

        prompt = prompt_template.format(
            video_title=video_title,
            video_description=video_description,
            transcript_text=transcript_text,
            csv_row_data=csv_row_data,
        )

        response = model.generate_content(prompt)

        with open(summary_path, "w") as f:
            f.write(response.text)

        logging.info(
            f"Successfully generated summary for {video_id} and saved to {summary_path}"
        )

    except Exception as e:
        logging.error(f"Failed to process video {video_id}: {e}")


def main():
    """Main function to summarize video transcripts."""
    args = parse_args()

    try:
        model = initialize_model(args.config_path)
        with open(args.prompt_path, "r") as f:
            prompt_template = f.read()
        os.makedirs(args.output_dir, exist_ok=True)
        df = pd.read_csv(args.csv_path)
        if args.limit:
            df = df.head(args.limit)
    except Exception as e:
        logging.error(f"Initialization failed: {e}")
        sys.exit(1)

    for _, row in df.iterrows():
        process_video(row, model, prompt_template, args)


if __name__ == "__main__":
    main()
