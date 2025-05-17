# Multilingual News Summarizer

A Streamlit application that provides AI-powered news summaries in multiple languages using Sutra's advanced language capabilities and real-time web search.

## Features

- **Multilingual Support**: Get news summaries in any language you specify
- **Real-time Information**: Uses DuckDuckGo search to fetch the latest information
- **User-friendly Interface**: Clean, intuitive UI with sample queries
- **Customizable**: Toggle search functionality and tool call visibility

## How It Works

1. Enter your Sutra API key
2. Type a query specifying what news you want summarized and in which language
3. The app searches for recent information using DuckDuckGo
4. Sutra AI processes the information and generates a summary in your requested language

## Sample Queries

- "Summarize the latest global economic news in Hindi"
- "What are the recent tech industry developments? Respond in French."
- "Summarize today's top sports headlines in German"

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multilingual-news-summarizer.git
cd multilingual-news-summarizer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Requirements

- Python 3.7+
- Streamlit
- Requests
- python-dotenv
- Agno agent
- DuckDuckGo Search

## Configuration

Create a `.env` file in the root directory with your Sutra API key:

```
SUTRA_API_KEY=your_api_key_here
```

Alternatively, you can enter your API key directly in the app's sidebar.

## Screenshots

![App Screenshot](https://example.com/screenshot.png)

## License

MIT

## Credits

Built with [Sutra](https://www.two.ai/sutra/api) and [Streamlit](https://streamlit.io/).
